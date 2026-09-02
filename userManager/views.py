from django.shortcuts import render

# Create your views here.
def login(request):
    return render(request, "users/login.html")


def logout(request):
    pass

def register(request):
    return render(request, "users/register.html")

def info_about_user(request, user_id):
    return render(request, "users/user-details.html")

def edit_profile(request, user_id):
    return render(request, "users/edit_profile.html")

def change_password(request):
    return render(request, "users/change_password.html")

def participants(request):
    return render(request, "users/participants.html")