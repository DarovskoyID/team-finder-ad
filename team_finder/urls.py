from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', lambda request: redirect('projects/list/')),
    path('projects/', include('projectManager.urls', namespace='projects')),
    path('users/', include('userManager.urls', namespace='users')),

]
