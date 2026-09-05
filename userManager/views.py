import email

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from userManager.forms import RegistrationForm, LoginForm, EditProfileForm, ChangePasswordForm
from userManager.models import User


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
    data = {'form': form}
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

                    User.objects.create_user(
                        email=email, password=password, name=name, surname=surname)
                    return redirect('/users/login/')
    else:
        form = RegistrationForm()

    data = {'form': form}
    return render(request, "users/register.html", data)


def info_about_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    data = {'user': user, }
    return render(request, "users/user-details.html", data)


def edit_profile(request):

    if request.user.is_authenticated:
        user = request.user
        if request.method == "POST":
            form = EditProfileForm(request.POST, request.FILES)
            if form.is_valid():
                user.name = form.cleaned_data['name']
                user.surname = form.cleaned_data['surname']
                if form.cleaned_data['avatar']:
                    user.avatar = form.cleaned_data['avatar']
                user.about = form.cleaned_data['about']
                user.phone = form.cleaned_data['phone']
                user.github_url = form.cleaned_data['github_url']

                user.save()

                return redirect('/users/'+str(user.id))

        elif request.method == "GET":
            form = EditProfileForm(initial={
                'name': user.name,
                'surname': user.surname,
                'avatar': user.avatar,
                'about': user.about,
                'phone': user.phone,
                'github_url': user.github_url,

            })

        data = {'form': form}
        return render(request, "users/edit_profile.html", data)
    else:
        return redirect('/projects/list/')


def change_password(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = ChangePasswordForm(data=request.POST)
            if form.is_valid():
                current_password = form.cleaned_data['current_password']
                new_password1 = form.cleaned_data['new_password1']
                new_password2 = form.cleaned_data['new_password2']
                if request.user.check_password(current_password):
                    if new_password1 == new_password2:
                        try:
                            validate_password(new_password1)
                        except ValidationError as error:
                            form.add_error('new_password1', error)
                        else:
                            request.user.set_password(new_password1)
                            request.user.save()
                            update_session_auth_hash(request, request.user)
                            return redirect('/projects/list/')
                    else:
                        form.add_error('new_password2',
                                       'Пароль не совпадает')
                else:
                    form.add_error('current_password', 'Это не ваш пароль')
        else:
            form = ChangePasswordForm()
        data = {'form': form}
        return render(request, "users/change_password.html", data)
    else:
        return redirect('/users/login/')


def participants(request):
    participants = User.objects.all().filter(
        is_active=True).order_by('-date_joined')

    paginator = Paginator(participants, 12)
    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    data = {'page_obj': page_obj}

    return render(request, "users/participants.html", data)
