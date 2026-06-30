from django.urls import path, include
from rest_framework.routers import DefaultRouter
<<<<<<< HEAD
from .views import NoteViewSet, NoteAttachmentViewSet , TagViewSet
=======
from .views import NoteViewSet, NoteAttachmentViewSet
>>>>>>> 9189de6f6e0efed64d09b8bbd24ee2ef0702541e

# استفاده از DefaultRouter یا SimpleRouter عالی است.
# DefaultRouter مزیتش این است که یک API Root در مرورگر به تو نشان می‌دهد.
router = DefaultRouter()

# ثبت ViewSetها
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'attachments', NoteAttachmentViewSet, basename='attachment')
<<<<<<< HEAD
router.register(r'tags', TagViewSet, basename='tag')
=======
>>>>>>> 9189de6f6e0efed64d09b8bbd24ee2ef0702541e

urlpatterns = [
    # تمام Routeهای تولید شده توسط Router اینجا قرار می‌گیرند
    path('', include(router.urls)),
]
