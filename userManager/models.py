from django.db import models

from userManager.avatars import create_avatar

from team_finder.validators import (
    normalize_phone,
    validate_github_url,
    validate_phone,
)
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("email is required")
        else:
            email = self.normalize_email(email)
            user = self.model(email=email, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, null=False, blank=False)
    name = models.CharField(null=False, blank=False, max_length=124)
    surname = models.CharField(
        null=False, blank=False, max_length=124
    )
    avatar = models.ImageField(
        upload_to="avatars/", null=True, blank=True
    )
    phone = models.CharField(
        null=True,
        blank=True,
        max_length=12,
        unique=True,
        validators=[validate_phone],
    )
    github_url = models.URLField(
        null=True,
        blank=True,
        validators=[validate_github_url],
    )
    about = models.TextField(null=True, blank=True, max_length=256)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    def clean(self):
        super().clean()
        self.phone = normalize_phone(self.phone)

    def save(self, *args, **kwargs):
        self.phone = normalize_phone(self.phone)
        if not self.avatar:
            self.avatar = create_avatar(self.name)
            if kwargs.get("update_fields") is not None:
                kwargs["update_fields"] = {
                    *kwargs["update_fields"],
                    "avatar",
                }
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
