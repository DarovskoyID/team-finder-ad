from django import forms

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.password_validation import validate_password

from team_finder.validators import normalize_phone
from userManager.models import User


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(
        label="Пароль", widget=forms.PasswordInput
    )


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")
        labels = {"name": "Имя", "surname": "Фамилия"}

    def clean_email(self):
        return User.objects.normalize_email(
            self.cleaned_data["email"]
        )

    def clean(self):
        data = super().clean()
        if data.get("password"):
            candidate = User(
                **{
                    key: data.get(key, "")
                    for key in ("email", "name", "surname")
                }
            )
            try:
                validate_password(data["password"], candidate)
            except forms.ValidationError as error:
                self.add_error("password", error)
        return data

    def save(self):
        return User.objects.create_user(**self.cleaned_data)


class EditProfileForm(forms.ModelForm):
    def clean_phone(self):
        return normalize_phone(self.cleaned_data.get("phone"))

    class Meta:
        model = User
        fields = (
            "avatar",
            "name",
            "surname",
            "about",
            "phone",
            "github_url",
        )
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "about": "О себе, только хорошее",
            "phone": "Телефон",
            "github_url": "GitHub",
        }
        widgets = {"about": forms.Textarea(attrs={"rows": 5})}


class ChangePasswordForm(PasswordChangeForm):
    pass
