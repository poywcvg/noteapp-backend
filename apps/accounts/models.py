from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _ # برای استفاده از متن‌های ترجمه شده

class UserManager(BaseUserManager):
    def create_user(self, username, email=None, phone_number=None, password=None, **extra_fields):
        if not username:
            raise ValueError(_('Username is Required'))
        
        email = self.normalize_email(email)
        user = self.model(
            username=username, 
            email=email, 
            phone_number=phone_number, 
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user 

    def create_superuser(self, username, password=None, **extra_fields):
        # اطمینان از اینکه is_staff و is_superuser حتما True هستند
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))

        return self.create_user(username, password=password, **extra_fields)

# --------------------------------------------------------------------------
# User Model
# --------------------------------------------------------------------------

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with additional fields like phone_number and image.
    """
    username = models.CharField(_('username'), max_length=150, unique=True)
    email = models.EmailField(_('email address'), blank=True, null=True)
    first_name = models.CharField(_('first name'), max_length=100, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=100, blank=True, null=True)
    phone_number = models.CharField(_('phone number'), max_length=15, blank=True, null=True, unique=True)
    
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False) # Essential for Admin access
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    image = models.ImageField(_('avatar'), upload_to='avatars/', blank=True, null=True)
    
    # --- اضافه کردن فیلد نقش (Role) ---
    # این فیلد می تواند یک CharField با choices باشد یا یک ForeignKey به مدل Role
    # برای شروع، از CharField ساده استفاده می کنیم. اگر نیاز به مدیریت پرمیژن های دقیق تر بود، Foreign Key بهترین گزینه است.
    ROLE_CHOICES = (
        ('admin', _('Admin')),
        ('viewer', _('Viewer')),
        # می توانید نقش های بیشتری اضافه کنید
    )
    role = models.CharField(
        _('role'), 
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='viewer', # پیش فرض برای کاربران جدید
        help_text=_('Designates the user\'s role in the system.'),
    )
    # -----------------------------------

    objects = UserManager()

    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS را معمولا برای فیلدهایی که در create_user لازم هستند ولی در USERNAME_FIELD نیستند، استفاده می کنند.
    # برای create_superuser، فیلدهایی که setdefault می شوند، نیازی به اینجا ندارند.
    # اگر می خواستید email را برای create_user الزامی کنید، اینجا باید email را اضافه می کردید.
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'phone_number', 'role'] # برای اطمینان از پر شدن فیلدهای مهم در ساخت دستی یا از طریق ادمین

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.username
    
    # اگر بخواهید از پرمیژن های سفارشی روی نقش ها استفاده کنید، توابع get_role_permissions و has_role را اضافه کنید.
    # اما برای شروع، is_staff و is_superuser و fieldset های ادمین کافی هستند.
