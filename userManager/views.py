from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from userManager.forms import RegistrationForm, LoginForm, EditProfileForm
from userManager.models import User


# Create your views here.
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('/projects/list/')
            else:
                form.add_error(None, "Невереный email или пароль")
    else:
        form = LoginForm()
    data = {'form' : form}
    return render(request, "users/login.html", data)


def logout_view(request):
    logout(request)
    return redirect('/projects/list/')


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            name = form.cleaned_data['name']
            surname = form.cleaned_data['surname']

            if User.objects.filter(email=email).exists():
                form.add_error('email',
                               'Пользователь с таким email существует, авторизуйтесь если это ваш email ;)')
            else:
                try:
                    validate_password(password)
                except ValidationError as error:
                    form.add_error('password', error)
                else:

                    user = User.objects.create_user(email=email, password=password, name=name, surname=surname)
                    login(request, user)
                    return redirect('/projects/list/')
    else:
        form = RegistrationForm()

    data = {'form': form}
    return render(request, "users/register.html", data)

def info_about_user(request, user_id):
    data = {'user' : User.objects.get(pk=user_id),}
    return render(request, "users/user-details.html", data)

def edit_profile(request):
    form = EditProfileForm(request.POST, request.FILES)
    if request.user.is_authenticated:
        if request.method == "POST":
            if form.is_valid():
                user = request.user
                user.name = form.cleaned_data['name']
                user.surname = form.cleaned_data['surname']
                user.avatar = form.cleaned_data['avatar']
                user.about = form.cleaned_data['about']
                user.phone = form.cleaned_data['phone']
                user.github = form.cleaned_data['github']

                user.save()
    else:
        return redirect('/projects/list/')

    data = {'form' : form}
    return render(request, "users/edit_profile.html", data)

def change_password(request):
    return render(request, "users/change_password.html")

def participants(request):
    participants = User.objects.all()

    if (request.user.is_authenticated):
        participants = participants.filter(is_active=True).exclude(email=request.user.email)

    paginator = Paginator(participants, 12)
    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    data = {'page_obj': page_obj}

    return render(request, "users/participants.html", data)