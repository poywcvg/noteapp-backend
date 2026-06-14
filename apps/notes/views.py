from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Note, NoteAttachment
from .serializers import (
    NoteDetailSerializer,
    NoteListSerializer,
    NoteAttachmentSerializer
)
from .permissions import IsOwner


class NoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwner]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "content", "tags__name"]
    ordering_fields = ["updated_at", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return NoteListSerializer

        return NoteDetailSerializer

    def get_queryset(self):
        queryset = (
            Note.objects
            .filter(user=self.request.user)
            .select_related("user")
            .prefetch_related("tags", "attachments")
        )

        if self.action == "deleted":
            return queryset.filter(is_deleted=True)

        if self.action == "archived":
            return queryset.filter(is_archived=True, is_deleted=False)

        if self.action in ["restore", "hard_delete"]:
            return queryset.filter(is_deleted=True)

        return queryset.filter(is_deleted=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save(update_fields=["is_deleted", "deleted_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def restore(self, request, pk=None):
        note = get_object_or_404(
            Note,
            id=pk,
            user=request.user,
            is_deleted=True
        )

        note.is_deleted = False
        note.deleted_at = None
        note.save(update_fields=["is_deleted", "deleted_at"])

        return Response({"status": "restored"})

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def archive(self, request, pk=None):
        note = self.get_object()
        note.is_archived = True
        note.archived_at = timezone.now()
        note.is_deleted = False
        note.save(update_fields=["is_archived", "archived_at", "is_deleted"])
        return Response({"status": "archived"})

    @action(detail=True, methods=["delete"])
    @transaction.atomic
    def hard_delete(self, request, pk=None):
        note = get_object_or_404(
            Note,
            id=pk,
            user=request.user,
            is_deleted=True
        )

        note.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def deleted(self, request):
        return self._list_queryset(self.get_queryset())

    @action(detail=False, methods=["get"])
    def archived(self, request):
        return self._list_queryset(self.get_queryset())

    def _list_queryset(self, queryset):
        serializer = NoteListSerializer(queryset, many=True)
        return Response(serializer.data)


class NoteAttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = NoteAttachmentSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return (
            NoteAttachment.objects
            .filter(note__user=self.request.user)
            .select_related("note")
        )

    def perform_create(self, serializer):
        note_id = self.request.data.get("note")

        note = get_object_or_404(
            Note,
            id=note_id,
            user=self.request.user
        )

        serializer.save(note=note)