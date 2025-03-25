from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
from django.db import models
from django.utils.timezone import now
from django.contrib.auth import get_user_model

# Choices for level and status fields
LEVEL_CHOICES = [
    (1, "Simple"),
    (2, "Uploader"),
    (3, "Multiple"),
    (4, "Admin"),
]

STATUS_CHOICES = [
    ("A", "Active"),
    ("B", "Blocked"),
    ("C", "Closed"),
]

class SysUsersManager(BaseUserManager):

    def create_user(self, login, password=None, created_by=None, **extra_fields):
        """Create and return a regular user."""
        if not login:
            raise ValueError("The Login field must be set")
        
        extra_fields.setdefault("status", "A")  # Default status is Active
        user = self.model(login=login, created_by=created_by, **extra_fields)
        if password:
            user.set_password(password)  
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None, **extra_fields):
        """Create and return a superuser with admin permissions."""
        extra_fields.setdefault("level", 4)  # Superuser is always level 4 (Admin)
        extra_fields.setdefault("status", "A")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(login, password, **extra_fields)

class SysUsers(AbstractBaseUser, PermissionsMixin):
    cb_id = models.IntegerField(null=False, unique=True)  # Unique, not nullable
    fio = models.CharField(max_length=250)
    level = models.IntegerField(choices=LEVEL_CHOICES, default=1)
    login = models.CharField(max_length=150, unique=True)  # Unique and not nullable
    created_by = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={"is_superuser": True}
    )  # Can only be created by a superuser
    created_at = models.DateTimeField(default=now)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="A")
    
    is_staff = models.BooleanField(default=False)  # Required for admin panel access
    is_active = models.BooleanField(default=True)  # Needed for authentication

    objects = SysUsersManager()
    
    USERNAME_FIELD = "login"  # Login is used as the unique identifier
    REQUIRED_FIELDS = ["fio", "level", "cb_id"]  # Required fields for superuser creation

    def __str__(self):
        return f"{self.fio} ({self.login})"
    
    def creater(self):
        return self.created_by.cb_id
    
    class Meta: 
        verbose_name = 'System User'
        verbose_name_plural = 'System Users'
