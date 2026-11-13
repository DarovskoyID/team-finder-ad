from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from team_finder.constants import (
    ABOUT_MAX_LENGTH,
    NAME_MAX_LENGTH,
    PHONE_MAX_LENGTH,
)
from team_finder.validators import (
    normalize_phone,
    validate_github_url,
    validate_phone,
)
from users.avatars import create_avatar


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("email is required")
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
    email = models.EmailField("Email", unique=True)
    name = models.CharField("Имя", max_length=NAME_MAX_LENGTH)
    surname = models.CharField("Фамилия", max_length=NAME_MAX_LENGTH)
    avatar = models.ImageField(
        "Аватар", upload_to="avatars/", null=True, blank=True
    )
    phone = models.CharField(
        "Телефон",
        null=True,
        blank=True,
        max_length=PHONE_MAX_LENGTH,
        unique=True,
        validators=[validate_phone],
    )
    github_url = models.URLField(
        "GitHub",
        null=True,
        blank=True,
        validators=[validate_github_url],
    )
    about = models.TextField(
        "О себе", null=True, blank=True, max_length=ABOUT_MAX_LENGTH
    )
    is_active = models.BooleanField("Активен", default=True)
    is_staff = models.BooleanField("Доступ в админку", default=False)
    date_joined = models.DateTimeField(
        "Дата регистрации", auto_now_add=True
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        ordering = ("-date_joined", "-pk")
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def clean(self):
        super().clean()
        validate_phone(self.phone)
        self.phone = normalize_phone(self.phone)

    def save(self, *args, **kwargs):
        validate_phone(self.phone)
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
