from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path

from projectManager import views as project_views

app_name = 'projects'

urlpatterns = [
    path('list/', project_views.list_view, name='list'),
    path('create-project/', project_views.create_project, name='create_project'),
    path('<int:project_id>/', project_views.project_detail,
         name='project_detail'),
    path('<int:project_id>/edit/',
         project_views.project_edit, name='project_edit'),
    path('<int:project_id>/complete/',
         project_views.project_complete, name='project_complete'),
    path('<int:project_id>/toggle-participate/',
         project_views.toggle_participate, name='toggle_participate'),
    path('skills/', project_views.skills_search, name='skills_search'),
    path('<int:project_id>/skills/add/',
         project_views.skill_add, name='skill_add'),
    path('<int:project_id>/skills/<int:skill_id>/remove/',
         project_views.skill_remove, name='skill_remove'),
]
