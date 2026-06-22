"""
URL configuration for noteapp2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from django.conf.urls.static import static
from django.conf import settings 
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # API routes
    path("auth/", include("apps.accounts.urls")),
    path("", include("apps.notes.urls")),
     path('', include('apps.accounts.urls')),
    path('', include('apps.notes.urls')),


    # مسیر دریافت فایل Schema (فرمت YAML/JSON)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # مسیر مشاهده داکیومنت به سبک Swagger (محبوب‌ترین حالت)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # مسیر مشاهده داکیومنت به سبک Redoc (یک استایل شیک دیگر)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

] + static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT)





