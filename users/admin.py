from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from users.models import SysUsers #, SysReportAccess

class SysUsersCreationForm(forms.ModelForm):
    """Custom form for creating new users in the admin panel."""
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = SysUsers
        fields = ("login", "fio", "level", "cb_id", "status")

    def clean_password2(self):
        """Ensure passwords match."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match!")
        return password2

    def save(self, commit=True):
        """Save the user with a hashed password."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class SysUsersChangeForm(forms.ModelForm):
    """Custom form for editing users in the admin panel."""
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=False)

    class Meta:
        model = SysUsers
        fields = ("login", "fio", "level", "cb_id", "status", "is_active", "is_staff", "created_by")

    def save(self, commit=True):
        """Ensure password is hashed when changed."""
        user = super().save(commit=False)
        if self.cleaned_data["password"]:
            user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class SysUsersAdmin(UserAdmin):
    """Admin settings for SysUsers."""
    form = SysUsersChangeForm
    add_form = SysUsersCreationForm
    list_display = ("login", "fio", "level", "cb_id", "status", "is_active", "is_staff", "created_by")
    list_filter = ("level", "status", "is_active", "is_staff")
    list_display_links = ("login", "fio", "level", "cb_id", "status", "is_active", "is_staff", "created_by")
    search_fields = ("login", "fio")
    ordering = ("cb_id",)
    
    fieldsets = (
        (None, {"fields": ("login", "password")}),
        ("Personal Info", {"fields": ("fio", "cb_id", "level", "status")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Created By", {"fields": ("created_by",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("login", "fio", "cb_id", "level", "status", "password1", "password2", "is_active", "is_staff"),
        }),
    )

    def save_model(self, request, obj, form, change):
        """Ensure created_by is set to the current superuser when creating a user."""
        if not obj.pk:  # Only set created_by when creating a new user
            obj.created_by = request.user if request.user.is_superuser else None
        obj.save()

admin.site.register(SysUsers, SysUsersAdmin)

