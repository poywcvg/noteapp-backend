from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _ # برای ترجمه

User = get_user_model()


# ----------------------------------------
# User Serializer (برای نمایش اطلاعات)
# ----------------------------------------

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "image",
            "date_joined",
            "role", # اضافه کردن فیلد role برای نمایش
            "is_staff", # اضافه کردن is_staff برای نمایش وضعیت ادمین
        ]
        # read_only_fields برای فیلدهایی است که نباید از طریق API تغییر کنند
        read_only_fields = [
            "id", 
            "username", 
            "date_joined", 
            "role", # اگر role فقط از طریق ادمین تغییر کند، اینجا اضافه کنید
            "is_staff", # اگر is_staff فقط از طریق ادمین تغییر کند، اینجا اضافه کنید
        ]

# ----------------------------------------
# Register Serializer
# ----------------------------------------

class RegisterSerializer(serializers.ModelSerializer):
    # تعریف فیلدهای لازم برای ثبت نام
    password = serializers.CharField(write_only=True, min_length=6, required=True, help_text=_("Enter a password of at least 6 characters."))
    password2 = serializers.CharField(write_only=True, required=True, help_text=_("Confirm your password."))
    
    # اضافه کردن فیلدهایی که در مدل User هستند ولی از طریق فرم ثبت نام باید پر شوند
    email = serializers.EmailField(required=False) # فرض می کنیم ایمیل اختیاری است
    phone_number = serializers.CharField(max_length=15, required=False) # فرض می کنیم شماره موبایل اختیاری است
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)

    class Meta:
        model = User
        # فیلدهایی که هنگام ثبت نام از کاربر دریافت می کنیم
        fields = [
            "username",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "password",
            "password2",
        ]

    def validate(self, attrs):
        # چک کردن تطابق رمز عبور
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError({"password": _("Passwords do not match.")})
        
        # چک کردن اینکه آیا username قبلا وجود دارد (اگر مدل User شما unique است)
        if User.objects.filter(username=attrs.get("username")).exists():
            raise serializers.ValidationError({"username": _("This username is already taken.")})
            
        # می توانید چک های بیشتری اینجا اضافه کنید، مثلا برای ایمیل یا شماره موبایل

        return attrs

    def create(self, validated_data):
        # حذف password2 چون برای ساخت کاربر لازم نیست
        validated_data.pop("password2", None) 

        # استخراج مقادیر و پاس دادن به create_user
        username = validated_data.get("username")
        email = validated_data.get("email")
        phone_number = validated_data.get("phone_number")
        password = validated_data.get("password")
        first_name = validated_data.get("first_name")
        last_name = validated_data.get("last_name")
        
        # از create_user سفارشی خودتان استفاده می کنید
        # این تابع نقش 'viewer' را به طور پیش فرض به کاربر می دهد
        user = User.objects.create_user(
            username=username,
            email=email,
            phone_number=phone_number,
            password=password,
            first_name=first_name,
            last_name=last_name,
            # role = 'viewer' # نقش پیش فرض در مدل تعریف شده است، نیازی به پاس دادن اینجا نیست مگر بخواهید تغییر دهید
        )
        
        return user


# ----------------------------------------
# Login Serializer (JWT Compatible)
# ----------------------------------------

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    # اضافه کردن فیلد برای نگهداری توکن های JWT
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        # استفاده از authenticate دیفالت Django
        user = authenticate(
            request=self.context.get('request'), # Pass request to authenticate if needed
            username=username,
            password=password
        )

        if not user:
            # بررسی اینکه آیا خطای کاربر یا رمز عبور است
            # برای امنیت بیشتر، پیام خطا را کلی نگه دارید
            raise serializers.ValidationError(_("Invalid username or password."))

        if not user.is_active:
            raise serializers.ValidationError(_("User account is disabled."))
        
        # اگر کاربر فعال و معتبر بود، توکن های JWT را ایجاد کنید
        refresh = RefreshToken.for_user(user)
        attrs["access_token"] = str(refresh.access_token)
        attrs["refresh_token"] = str(refresh)
        
        # ذخیره کاربر برای استفاده در متد save
        attrs["user"] = user
        return attrs

    # متد save برای این سریالایزر معنی خاصی ندارد چون فقط token را برمیگرداند
    # می توانید آن را حذف کنید یا برای اطمینان، آن را نگه دارید
    def save(self, **kwargs):
        # این سریالایزر فقط توکن ها را برمیگرداند، بنابراین متد save نیازی به کاری ندارد
        # اما می توانید آن را برای بازگرداندن داده های اعتبارسنجی شده (که شامل توکن ها هستند) استفاده کنید
        # اگر نیازی به این متد نیست، می توانید آن را حذف کنید.
        pass


# ----------------------------------------
# Logout Serializer
# ----------------------------------------

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

    def validate(self, attrs):
        self.refresh_token = attrs.get('refresh')
        return attrs

    def save(self, **kwargs):
        # اطمینان از اینکه توکن معتبر است قبل از blacklist کردن
        try:
            token = RefreshToken(self.refresh_token)
            token.blacklist()
        except Exception as e:
            # اگر توکن نامعتبر یا منقضی شده بود، خطا بده
            raise serializers.ValidationError({"refresh": _("Invalid or expired token.")}) from e

        return {"detail": _("Successfully logged out.")}
