<<<<<<< HEAD
# apps/notes/api/views.py
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from .models import Note, NoteAttachment, Tag
from .serializers import (
    NoteDetailSerializer,
    NoteListSerializer,
    NoteAttachmentSerializer,
    TagSerializer
=======
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
>>>>>>> 9189de6f6e0efed64d09b8bbd24ee2ef0702541e
)
from .permissions import IsOwner


<<<<<<< HEAD
# ==================== Note ViewSet ====================
class NoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet برای مدیریت یادداشت‌ها
    پشتیبانی از: CRUD, آرشیو, حذف نرم, عملیات گروهی
    """
=======
class NoteViewSet(viewsets.ModelViewSet):
>>>>>>> 9189de6f6e0efed64d09b8bbd24ee2ef0702541e
    permission_classes = [IsOwner]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "content", "tags__name"]
    ordering_fields = ["updated_at", "created_at"]

    def get_serializer_class(self):
<<<<<<< HEAD
        return NoteListSerializer if self.action == "list" else NoteDetailSerializer

    def get_queryset(self):
        """
        🟢 تغییر ۱: اصلاح کوئری‌ست برای حالت‌های مختلف
        - جلوگیری از نمایش یادداشت‌های آرشیو شده در لیست اصلی
        - فرانت‌کار نیازی به تغییر ندارد چون خروجی نهایی یکسان است
        """
=======
        if self.action == "list":
            return NoteListSerializer

        return NoteDetailSerializer

    def get_queryset(self):
>>>>>>> 9189de6f6e0efed64d09b8bbd24ee2ef0702541e
        queryset = (
            Note.objects
            .filter(user=self.request.user)
            .select_related("user")
            .prefetch_related("tags", "attachments")
        )

<<<<<<< HEAD
        # سطل زباله: فقط یادداشت‌های حذف شده
        if self.action == "deleted":
            return queryset.filter(is_deleted=True)

        # یادداشت‌های آرشیو شده: فقط آرشیو شده‌هایی که حذف نشدن
        if self.action == "archived":
            return queryset.filter(is_archived=True, is_deleted=False)

        # عملیات بازیابی و حذف دائمی فقط روی یادداشت‌های حذف شده
        if self.action in ["restore", "hard_delete"]:
            return queryset.filter(is_deleted=True)

        # 🟢 تغییر: حالت پیش‌فرض - فقط یادداشت‌های فعال (نه حذف شده، نه آرشیو)
        # قبلاً این خط نبود و همه رو برمی‌گردوند
        return queryset.filter(is_deleted=False, is_archived=False)

    def perform_create(self, serializer):
        """ذخیره یادداشت با کاربر فعلی"""
        serializer.save(user=self.request.user)

    # ==================== عملیات حذف ====================

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        🟢 تغییر ۲: حذف نرم (Soft Delete)
        - یادداشت به سطل زباله منتقل میشه
        - بدون تغییر در خروجی (همان 204 No Content)
        """
=======
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
>>>>>>> 9189de6f6e0efed64d09b8bbd24ee2ef0702541e
        instance = self.get_object()
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save(update_fields=["is_deleted", "deleted_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)

<<<<<<< HEAD
    # ==================== عملیات تکی ====================

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def restore(self, request, pk=None):
        """
        🟢 تغییر ۳: بازیابی یادداشت از سطل زباله
        - is_deleted = False
        - is_archived = False (خروج از آرشیو هم به صورت خودکار)
        - خروجی بدون تغییر: {"status": "restored"}
        - فرانت‌کار نیازی به تغییر ندارد
        """
        note = self.get_object()
        note.is_deleted = False
        note.deleted_at = None
        # 🟢 تغییر: اگر یادداشت آرشیو شده بود، از آرشیو خارج میشه
        # این کار باعث میشه یادداشت کاملاً به حالت عادی برگرده
        note.is_archived = False
        note.archived_at = None
        note.save(update_fields=["is_deleted", "deleted_at", "is_archived", "archived_at"])
=======
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

>>>>>>> 9189de6f6e0efed64d09b8bbd24ee2ef0702541e
        return Response({"status": "restored"})

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def archive(self, request, pk=None):
<<<<<<< HEAD
        """
        آرشیو کردن یادداشت
        - is_archived = True
        - اگر حذف شده بود، از حذف خارج میشه
        - خروجی بدون تغییر: {"status": "archived"}
        """
        note = self.get_object()
        note.is_archived = True
        note.archived_at = timezone.now()
        # اگر یادداشت حذف شده بود، از حذف خارج میشه
        note.is_deleted = False
        note.deleted_at = None
        note.save(update_fields=["is_archived", "archived_at", "is_deleted", "deleted_at"])
        return Response({"status": "archived"})

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def unarchive(self, request, pk=None):
        """
        🟢 تغییر ۴: خروج از آرشیو (API جدید - اختیاری)
        - is_archived = False
        - فرانت‌کار می‌تونه از این API استفاده کنه یا نه
        - خروجی: {"status": "unarchived"}
        """
        note = self.get_object()
        note.is_archived = False
        note.archived_at = None
        note.save(update_fields=["is_archived", "archived_at"])
        return Response({"status": "unarchived"})

    @action(detail=True, methods=["delete"])
    @transaction.atomic
    def hard_delete(self, request, pk=None):
        """
        حذف دائمی یادداشت (فقط از سطل زباله)
        - فقط یادداشت‌های حذف شده قابل حذف دائمی هستند
        - خروجی بدون تغییر: 204 No Content
        """
        note = self.get_object()
        if not note.is_deleted:
            return Response(
                {"error": "Note must be in trash to be permanently deleted."},
                status=status.HTTP_400_BAD_REQUEST
            )
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ==================== لیست‌های ویژه ====================

    @action(detail=False, methods=["get"])
    def deleted(self, request):
        """
        لیست یادداشت‌های حذف شده (سطل زباله)
        - خروجی بدون تغییر
        """
=======
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
>>>>>>> 9189de6f6e0efed64d09b8bbd24ee2ef0702541e
        return self._list_queryset(self.get_queryset())

    @action(detail=False, methods=["get"])
    def archived(self, request):
<<<<<<< HEAD
        """
        لیست یادداشت‌های آرشیو شده
        - خروجی بدون تغییر
        """
        return self._list_queryset(self.get_queryset())

    def _list_queryset(self, queryset):
        """
        Helper برای سریالایز کردن کوئری‌ست‌های خاص
        🟢 تغییر: استفاده از get_serializer برای انعطاف‌پذیری بیشتر
        """
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # ==================== عملیات گروهی (Bulk Actions) ====================

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def bulk_delete(self, request):
        """
        🟢 تغییر ۵: حذف نرم گروهی (API جدید)
        - دریافت: {'ids': [1, 2, 3, ...]}
        - خروجی: {'status': 'success', 'deleted_count': N}
        """
        ids = request.data.get('ids', [])
        
        # اعتبارسنجی ورودی
        if not ids:
            return Response(
                {"error": "No note IDs provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not isinstance(ids, list):
            return Response(
                {"error": "ids must be a list."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # فقط یادداشت‌های فعال (نه حذف شده)
        notes = Note.objects.filter(
            user=request.user,
            id__in=ids,
            is_deleted=False
        )
        
        deleted_count = notes.count()
        if deleted_count == 0:
            return Response(
                {"error": "No valid notes found to delete."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # حذف نرم
        now = timezone.now()
        notes.update(
            is_deleted=True,
            deleted_at=now,
            is_archived=False,
            archived_at=None
        )
        
        return Response({
            "status": "success",
            "message": f"{deleted_count} note(s) deleted successfully.",
            "deleted_count": deleted_count
        })

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def bulk_hard_delete(self, request):
        """
        🟢 تغییر ۶: حذف دائمی گروهی (API جدید)
        - فقط یادداشت‌های حذف شده (سطل زباله)
        - دریافت: {'ids': [1, 2, 3, ...]}
        - خروجی: {'status': 'success', 'deleted_count': N}
        """
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response(
                {"error": "No note IDs provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not isinstance(ids, list):
            return Response(
                {"error": "ids must be a list."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # فقط یادداشت‌های حذف شده
        notes = Note.objects.filter(
            user=request.user,
            id__in=ids,
            is_deleted=True
        )
        
        deleted_count = notes.count()
        if deleted_count == 0:
            return Response(
                {"error": "No deleted notes found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # حذف دائمی
        notes.delete()
        
        return Response({
            "status": "success",
            "message": f"{deleted_count} note(s) permanently deleted.",
            "deleted_count": deleted_count
        })

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def bulk_restore(self, request):
        """
        🟢 تغییر ۷: بازیابی گروهی (API جدید)
        - فقط یادداشت‌های حذف شده (سطل زباله)
        - دریافت: {'ids': [1, 2, 3, ...]}
        - خروجی: {'status': 'success', 'restored_count': N}
        """
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response(
                {"error": "No note IDs provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not isinstance(ids, list):
            return Response(
                {"error": "ids must be a list."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # فقط یادداشت‌های حذف شده
        notes = Note.objects.filter(
            user=request.user,
            id__in=ids,
            is_deleted=True
        )
        
        restored_count = notes.count()
        if restored_count == 0:
            return Response(
                {"error": "No deleted notes found to restore."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # بازیابی و خروج از آرشیو
        notes.update(
            is_deleted=False,
            deleted_at=None,
            is_archived=False,
            archived_at=None
        )
        
        return Response({
            "status": "success",
            "message": f"{restored_count} note(s) restored successfully.",
            "restored_count": restored_count
        })

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def bulk_archive(self, request):
        """
        🟢 تغییر ۸: آرشیو گروهی (API جدید)
        - فقط یادداشت‌های فعال (نه حذف شده، نه آرشیو)
        - دریافت: {'ids': [1, 2, 3, ...]}
        - خروجی: {'status': 'success', 'archived_count': N}
        """
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response(
                {"error": "No note IDs provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not isinstance(ids, list):
            return Response(
                {"error": "ids must be a list."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # فقط یادداشت‌های فعال
        notes = Note.objects.filter(
            user=request.user,
            id__in=ids,
            is_deleted=False,
            is_archived=False
        )
        
        archived_count = notes.count()
        if archived_count == 0:
            return Response(
                {"error": "No active notes found to archive."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # آرشیو
        now = timezone.now()
        notes.update(
            is_archived=True,
            archived_at=now
        )
        
        return Response({
            "status": "success",
            "message": f"{archived_count} note(s) archived successfully.",
            "archived_count": archived_count
        })


# ==================== Attachment ViewSet ====================
class NoteAttachmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet برای مدیریت پیوست‌های یادداشت
    """
=======
        return self._list_queryset(self.get_queryset())

    def _list_queryset(self, queryset):
        serializer = NoteListSerializer(queryset, many=True)
        return Response(serializer.data)


class NoteAttachmentViewSet(viewsets.ModelViewSet):
>>>>>>> 9189de6f6e0efed64d09b8bbd24ee2ef0702541e
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
<<<<<<< HEAD
=======

>>>>>>> 9189de6f6e0efed64d09b8bbd24ee2ef0702541e
        note = get_object_or_404(
            Note,
            id=note_id,
            user=self.request.user
        )
<<<<<<< HEAD
        serializer.save(note=note)


# ==================== Tag ViewSet ====================
@extend_schema(tags=['tags'])
class TagViewSet(viewsets.ModelViewSet):
    """
    🟢 تغییر ۹: اضافه شدن IsOwner به permission_classes
    - قبلاً فقط IsAuthenticated بود
    - الان کاربر فقط می‌تونه تگ‌های خودش رو مدیریت کنه
    """
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
=======

        serializer.save(note=note)
>>>>>>> 9189de6f6e0efed64d09b8bbd24ee2ef0702541e
