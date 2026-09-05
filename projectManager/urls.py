from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from projectManager import views as project_views

app_name = 'projects'

urlpatterns = [
    path('list/', project_views.list, name='list'),
    path('create-project/', project_views.create_project, name='create_project'),
    path('<int:project_id>/', project_views.project_detail, name='project_detail'),
    path('<int:project_id>/edit/', project_views.project_edit, name='project_edit'),
    path('<int:project_id>/complete/', project_views.project_complete, name='project_complete'),
]