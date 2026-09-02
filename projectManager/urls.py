from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from projectManager import views as project_views

app_name = 'projects'

urlpatterns = [
    path('list/', project_views.list, name='list'),
]