from projectManager.status import status
from django import forms

class ProjectCreateForm(forms.Form):
    name = forms.CharField(label='Название великой идеи', max_length=200)
    description = forms.CharField(label='Описание', widget=forms.Textarea(attrs={'rows': 10, 'cols': 200}))
    github_url = forms.CharField(label='GitHub URL')
    status = forms.ChoiceField(label="Статус проекта", choices=status)