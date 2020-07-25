from django import forms
from django.contrib.auth.forms import UserCreationForm

from captcha.fields import ReCaptchaField

from .models import *


class SignUpForm(UserCreationForm):
    captcha = ReCaptchaField()
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=150)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'email',)
