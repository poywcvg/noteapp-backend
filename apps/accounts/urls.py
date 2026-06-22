from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterAPIView,
    LoginAPIView,
    MeAPIView,
    LogoutAPIView
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="api-register"),
    path("login/", LoginAPIView.as_view(), name="api-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeAPIView.as_view(), name="api-me"),
    path("logout/", LogoutAPIView.as_view(), name="api_logout"),
]