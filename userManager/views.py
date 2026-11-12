from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
)
from userManager.forms import (
    RegistrationForm,
    LoginForm,
    EditProfileForm,
    ChangePasswordForm,
)
from userManager.models import User


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(
                request, username=email, password=password
            )

            if user is not None:
                login(request, user)
                return redirect("/projects/list/")
            else:
                form.add_error(None, "Неверный email или пароль")
    else:
        form = LoginForm()
    data = {"form": form}
    return render(request, "users/login.html", data)


def logout_view(request):
    logout(request)
    return redirect("/projects/list/")


def register(request):
    form = RegistrationForm(
        request.POST if request.method == "POST" else None,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("users:login")
    return render(request, "users/register.html", {"form": form})


def info_about_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    data = {
        "user": user,
    }
    return render(request, "users/user-details.html", data)


@login_required
def edit_profile(request):
    form = EditProfileForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
        instance=request.user,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(
            "users:info_about_user", user_id=request.user.pk
        )
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    form = ChangePasswordForm(
        request.user,
        data=request.POST if request.method == "POST" else None,
    )
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:info_about_user", user_id=user.pk)
    return render(
        request, "users/change_password.html", {"form": form}
    )


def participants(request):
    participants = User.objects.all().order_by("-date_joined", "-pk")

    paginator = Paginator(participants, 12)
    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    data = {"page_obj": page_obj}

    return render(request, "users/participants.html", data)
