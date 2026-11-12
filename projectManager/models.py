from django.db import models

from team_finder.validators import validate_github_url


from projectManager.status import status


class Skill(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        unique=True, null=False, blank=False, max_length=124
    )

    def __str__(self):
        return self.name


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(
        "userManager.User",
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(
        null=True,
        blank=True,
        validators=[validate_github_url],
    )
    status = models.CharField(choices=status, max_length=6)
    participants = models.ManyToManyField(
        "userManager.User",
        related_name="participated_projects",
        blank=True,
    )
    skills = models.ManyToManyField(
        Skill,
        related_name="projects",
        blank=True,
    )

    def __str__(self):
        return self.name
