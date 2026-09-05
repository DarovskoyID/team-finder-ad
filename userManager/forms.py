from cProfile import label

from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль')

class RegistrationForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль')
    name = forms.CharField(label="Имя", max_length=124)
    surname = forms.CharField(label="Фамилия", max_length=124)

class EditProfileForm(forms.Form):
    avatar = forms.ImageField(required=False)
    name = forms.CharField(label="Имя", max_length=124)
    surname = forms.CharField(label="Фамилия", max_length=124)
    about = forms.CharField(label="О себе, только хорошее",
                            max_length=256,
                            required=False,
                            widget=forms.Textarea(attrs={'rows': 5, 'max_length': 256}))
    phone = forms.CharField(label="Телефон", max_length=12, required=False)
    github = forms.URLField(label="GitHub", required=False)

class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(label="Текущий пароль")
    new_password1 = forms.CharField(label="Новый пароль")
    new_password2 = forms.CharField(label="Подтвердите новый пароль")








