from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, NoteAttachmentViewSet , TagViewSet

# استفاده از DefaultRouter یا SimpleRouter عالی است.
# DefaultRouter مزیتش این است که یک API Root در مرورگر به تو نشان می‌دهد.
router = DefaultRouter()

# ثبت ViewSetها
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'attachments', NoteAttachmentViewSet, basename='attachment')
router.register(r'tags', TagViewSet, basename='tag')

urlpatterns = [
    # تمام Routeهای تولید شده توسط Router اینجا قرار می‌گیرند
    path('', include(router.urls)),
]
