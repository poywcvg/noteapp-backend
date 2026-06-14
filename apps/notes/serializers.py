# apps/notes/api/serializers.py

from django.db import IntegrityError, transaction
from rest_framework import serializers

from .models import Note, Tag, NoteAttachment


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class NoteAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteAttachment
        fields = ["id", "file", "created_at"]
        read_only_fields = ["id", "created_at"]


class NoteListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = ["id", "title", "is_important", "is_archived", "updated_at", "tags"]
        read_only_fields = ["id", "updated_at"]


class NoteDetailSerializer(serializers.ModelSerializer):
    tags_input = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True
    )
    tags = TagSerializer(many=True, read_only=True)
    attachments = NoteAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = [
            "id",
            "title",
            "content",
            "is_important",
            "is_archived",
            "tags",
            "tags_input",
            "attachments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "tags", "attachments"]

    def validate_tags_input(self, value):
        if value == "":
            return value

        names = [n.strip() for n in value.split(",") if n.strip()]

        if len(names) != len(set(names)):
            # اگر خواستی می‌توانی به‌جای خطا، فقط deduplicate کنی
            names = list(dict.fromkeys(names))

        for name in names:
            if len(name) > 50:
                raise serializers.ValidationError(
                    f"Tag '{name}' exceeds 50 characters."
                )

        return ",".join(names)

    def _process_tags(self, instance, tags_input):
        # اگر field اصلاً ارسال نشده باشد، یعنی تگ‌ها را دست نزن
        if tags_input is serializers.empty:
            return

        # اگر عمداً خالی فرستاده شده، همه تگ‌ها پاک شوند
        if tags_input == "":
            instance.tags.clear()
            return

        tag_names = [n.strip() for n in tags_input.split(",") if n.strip()]
        tag_names = list(dict.fromkeys(tag_names))  # remove duplicates, preserve order

        tag_objects = []
        for name in tag_names:
            try:
                tag, _ = Tag.objects.get_or_create(
                    user=instance.user,
                    name=name,
                )
            except IntegrityError:
                tag = Tag.objects.get(user=instance.user, name=name)

            tag_objects.append(tag)

        instance.tags.set(tag_objects)

    @transaction.atomic
    def create(self, validated_data):
        tags_input = validated_data.pop("tags_input", serializers.empty)
        instance = Note.objects.create(**validated_data)
        self._process_tags(instance, tags_input)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        tags_input = validated_data.pop("tags_input", serializers.empty)
        instance = super().update(instance, validated_data)
        self._process_tags(instance, tags_input)
        return instance
