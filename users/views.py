from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render

from team_finder.utils import paginate
from users.forms import (
    RegistrationForm,
    LoginForm,
    EditProfileForm,
)
from users.models import User


def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        if user is not None:
            login(request, user)
            return redirect("projects:list")
        form.add_error(None, "Неверный email или пароль")
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def register(request):
    form = RegistrationForm(
        request.POST or None,
    )
    if not form.is_valid():
        return render(request, "users/register.html", {"form": form})
    form.save()
    return redirect("users:login")


def info_about_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    data = {
        "user": user,
    }
    return render(request, "users/user-details.html", data)


@login_required
def edit_profile(request):
    form = EditProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )
    if not form.is_valid():
        return render(
            request, "users/edit_profile.html", {"form": form}
        )
    form.save()
    return redirect("users:info_about_user", user_id=request.user.pk)


@login_required
def change_password(request):
    form = PasswordChangeForm(
        request.user,
        data=request.POST or None,
    )
    if not form.is_valid():
        return render(
            request, "users/change_password.html", {"form": form}
        )
    user = form.save()
    update_session_auth_hash(request, user)
    return redirect("users:info_about_user", user_id=user.pk)


def participants(request):
    return render(
        request,
        "users/participants.html",
        {"page_obj": paginate(request, User.objects.all())},
    )
