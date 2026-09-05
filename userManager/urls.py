from django.urls import path, include

from userManager import views as user_views

app_name = 'users'
urlpatterns = [
    path('login/',  user_views.login_view, name='login'),
    path('logout/', user_views.logout_view, name='logout'),
    path('register/', user_views.register, name='register'),
    path('<int:user_id>/', user_views.info_about_user, name='info_about_user'),
    path('change-password/', user_views.change_password, name='change_password'),
    path('edit-profile/', user_views.edit_profile, name='edit_profile'),
    path('list/', user_views.participants, name='participants'),

]
