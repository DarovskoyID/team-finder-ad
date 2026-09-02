from userManager.models import User
from django.db import models


from projectManager.status import status

class Skill(models.Model):
    name = models.CharField(null=False, blank=False, max_length=128)


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(null=True, blank=True)
    status = models.CharField(choices=status , max_length=6)
    participants = models.ManyToManyField(User, related_name='participated_projects')
    skills = models.ManyToManyField(Skill, related_name='skill')

    def __str__(self):
        return self.name
