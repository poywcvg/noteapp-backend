from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

# وارد کردن سریالایزرهای به‌روز شده
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    LogoutSerializer,
)
from django.contrib.auth import get_user_model # برای دسترسی به مدل User سفارشی

User = get_user_model() # دریافت مدل User سفارشی

# ----------------------------------------
# Register API
# ----------------------------------------

class RegisterAPIView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Allows any user to register.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Overrides the default create method to return JWT tokens and user data upon successful registration.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save() # این متد create را در serializer صدا می زند

        # پس از ثبت نام موفق، توکن های JWT را ایجاد و برگردانید
        refresh = RefreshToken.for_user(user)
        
        response_data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data, # اطلاعات کاربر ثبت نام شده
            "message": "User registered successfully!"
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)


# ----------------------------------------
# Login API (JWT)
# ----------------------------------------

class LoginAPIView(APIView):
    """
    API endpoint for user login.
    Returns JWT tokens upon successful authentication.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer # تعریف serializer_class برای استفاده در get_serializer

    def post(self, request, *args, **kwargs):
        """
        Handles user login, validates credentials, and returns JWT tokens.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # سریالایزر اعتبارسنجی شده شامل اطلاعات کاربر و توکن ها است
        user = serializer.validated_data.get("user")
        access_token = serializer.validated_data.get("access_token")
        refresh_token = serializer.validated_data.get("refresh_token")

        response_data = {
            "refresh": refresh_token,
            "access": access_token,
            "user": UserSerializer(user).data # اطلاعات کاربر لاگین شده
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


# ----------------------------------------
# Current User (Me) API
# ----------------------------------------

class MeAPIView(APIView):
    """
    API endpoint to get or update the current authenticated user's profile.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer # تعریف serializer_class برای استفاده در get_serializer

    def get(self, request):
        """
        Returns the profile data of the currently authenticated user.
        """
        # request.user به صورت خودکار توسط DRF/SimpleJWT از توکن استخراج می شود
        return Response(self.get_serializer(request.user).data)

    def put(self, request):
        """
        Updates the profile data of the currently authenticated user.
        Allows partial updates (e.g., updating only phone number or image).
        """
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True # برای امکان به‌روزرسانی جزئی (partial update)
        )
        serializer.is_valid(raise_exception=True)
        serializer.save() # متد save در UserSerializer فراخوانی می شود
        return Response(serializer.data)


# ----------------------------------------
# Logout API
# ----------------------------------------

class LogoutAPIView(APIView):
    """
    API endpoint for user logout.
    Requires authentication and a refresh token to invalidate the session.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer # تعریف serializer_class برای استفاده در get_serializer

    def post(self, request):
        """
        Handles user logout by blacklisting the provided refresh token.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save() # متد save در LogoutSerializer فراخوانی می شود (blacklist کردن توکن)
        
        # بازگرداندن پاسخ موفقیت آمیز بدون محتوا (204 No Content)
        return Response(status=status.HTTP_204_NO_CONTENT)
