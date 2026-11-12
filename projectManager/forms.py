from django import forms

from projectManager.models import Project


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название великой идеи",
            "description": "Описание",
            "github_url": "GitHub URL",
            "status": "Статус проекта",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 10}),
        }
