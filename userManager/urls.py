


from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from userManager import views as user_views

app_name = 'users'
urlpatterns = [
    path('login/',  user_views.login, name='login'),
    path('logout/', user_views.logout, name='logout'),
    path('register/', user_views.register, name='register'),
    path('<int:user_id>/', user_views.info_about_user, name='info_about_user'),
    path('change_password/', user_views.change_password, name='change_password'),
    path('edit-profile/', user_views.edit_profile, name='edit_profile'),
    path('list/', user_views.participants, name='participants'),

]
