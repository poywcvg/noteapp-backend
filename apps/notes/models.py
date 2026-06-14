from django.db import models
from django.conf import settings


# ----------------------------
#  Tag Model
# ----------------------------
class Tag(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tags",
        verbose_name="کاربر"
    )
    name = models.CharField(max_length=50, verbose_name="عنوان برچسب")

    class Meta:
        verbose_name = "برچسب"
        verbose_name_plural = "برچسب‌ها"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_user_tag"
            )
        ]
        indexes = [
            models.Index(fields=["user", "name"]),
        ]

    def __str__(self):
        return self.name



# ----------------------------
#  Custom Manager for Notes
# ----------------------------
class NoteQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False, is_archived=False)

    def archived(self):
        return self.filter(is_archived=True)

    def deleted(self):
        return self.filter(is_deleted=True)


# ----------------------------
#  Note Model
# ----------------------------
class Note(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes",
        verbose_name="کاربر"
    )

    tags = models.ManyToManyField(Tag, blank=True, related_name="notes", verbose_name="برچسب‌ها")

    title = models.CharField(max_length=200, verbose_name="عنوان")
    content = models.TextField(verbose_name="متن یادداشت")

    # Removed attachment field → use NoteAttachment model
    # attachment = models.FileField(...)

    is_important = models.BooleanField(default=False, verbose_name="مهم")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ ویرایش")

    # Soft Delete
    is_deleted = models.BooleanField(default=False, db_index=True, verbose_name="حذف شده")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ حذف")

    # Archive
    is_archived = models.BooleanField(default=False, db_index=True, verbose_name="آرشیو شده")
    archived_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ آرشیو")

    # received_from = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     related_name="received_notes",
    #     verbose_name="دریافت شده از"
    # )

    # objects = NoteQuerySet.as_manager()

    class Meta:
        verbose_name = "یادداشت"
        verbose_name_plural = "یادداشت‌ها"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "is_deleted"]),
            models.Index(fields=["user", "is_archived"]),
        ]

    def __str__(self):
        return self.title[:50]



# ----------------------------
#  Note Attachment Model
# ----------------------------
class NoteAttachment(models.Model):
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="یادداشت",
        db_index=True
    )
    file = models.FileField(upload_to="notes/attachments/", verbose_name="فایل")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "فایل ضمیمه"
        verbose_name_plural = "فایل‌های ضمیمه"
        indexes = [
            models.Index(fields=["note", "-created_at"]),
        ]

    def __str__(self):
        return f"Attachment for {self.note.title}"
