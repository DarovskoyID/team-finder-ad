from django.conf import settings
from django.db import models

from team_finder.constants import (
    NAME_MAX_LENGTH,
    PROJECT_NAME_MAX_LENGTH,
)
from team_finder.validators import validate_github_url


class Skill(models.Model):
    name = models.CharField(
        "Название", unique=True, max_length=NAME_MAX_LENGTH
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name


class Project(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Открыт"
        CLOSED = "closed", "Закрыт"

    name = models.CharField(
        "Название великой идеи", max_length=PROJECT_NAME_MAX_LENGTH
    )
    description = models.TextField("Описание", null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    created_at = models.DateTimeField(
        "Дата создания", auto_now_add=True
    )
    github_url = models.URLField(
        "GitHub URL",
        null=True,
        blank=True,
        validators=[validate_github_url],
    )
    status = models.CharField(
        "Статус проекта",
        choices=Status.choices,
        max_length=max(map(len, Status.values)),
        default=Status.OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Участники",
        related_name="participated_projects",
        blank=True,
    )
    skills = models.ManyToManyField(
        Skill,
        verbose_name="Навыки",
        related_name="projects",
        blank=True,
    )

    class Meta:
        ordering = ("-created_at", "-pk")
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    @property
    def is_open(self):
        return self.status == self.Status.OPEN

    def __str__(self):
        return self.name
