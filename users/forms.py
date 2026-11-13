from django import forms
from django.contrib.auth.password_validation import validate_password

from team_finder.validators import normalize_phone, validate_phone
from users.models import User


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
        phone = self.cleaned_data.get("phone")
        validate_phone(phone)
        return normalize_phone(phone)

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
