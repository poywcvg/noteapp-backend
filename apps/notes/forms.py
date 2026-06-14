from django import forms
from django.contrib.auth import get_user_model

from .models import Note, Tag

User = get_user_model()

BASE_INPUT = "w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 shadow-sm"
BASE_TEXTAREA = "w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 shadow-sm min-h-[140px]"


class NoteForm(forms.ModelForm):
    # تگ‌های موجود کاربر
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": BASE_INPUT}),
        label="برچسب‌ها",
    )

    # ورودی آزاد برای ساخت/انتخاب تگ جدید
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": BASE_INPUT,
                "placeholder": "مثلاً: کاری, فوری, مطالعه",
            }
        ),
        label="برچسب‌های جدید",
    )

    class Meta:
        model = Note
        fields = ["title", "content", "is_important", "tags", "tags_input" ]
        labels = {
            "title": "عنوان",
            "content": "متن یادداشت",
            "is_important": "مهم",
        
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": BASE_INPUT,
                    "placeholder": "مثلاً: ایده‌های پروژه",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": BASE_TEXTAREA,
                    "placeholder": "یادداشتت رو بنویس...",
                }
            ),
            "is_important": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 text-sky-600 border-gray-300 rounded",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["tags"].queryset = Tag.objects.filter(user=self.user).order_by("name")

        # اگر ویرایش می‌شود، تگ‌های فعلی را در فیلد tags و tags_input بگذار
        if self.instance.pk:
            self.fields["tags"].initial = self.instance.tags.all()
            self.fields["tags_input"].initial = ", ".join(
                [t.name for t in self.instance.tags.all()]
            )

                

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]
        labels = {"name": "عنوان برچسب"}
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": BASE_INPUT,
                    "placeholder": "مثلاً: کاری",
                }
            ),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'image']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # اعمال استایل‌های Tailwind به فیلدها
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 shadow-sm'
            })




class NoteShareForm(forms.Form):
    recipient = forms.ModelChoiceField(queryset=User.objects.none())

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["recipient"].queryset = User.objects.exclude(pk=user.pk) if user else User.objects.none()
