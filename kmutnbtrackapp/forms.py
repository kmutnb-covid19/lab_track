from django import forms
from django.template import loader
from django.core.mail import EmailMessage
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext, gettext_lazy as _

from .models import *


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=150)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'email',)


class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        user_data = {}
        protocol = context['protocol']
        domain = context['domain']
        uid64 = context['uid']
        token = context['token']
        lab_hash = context['lab_hash']
        user = context['user']
        username = user.username
        link = protocol + "://" + domain + "/reset/" + uid64 + '/' + token + "/?next=" + lab_hash
        user_data[to_email] = {'link': link, 'username': username}

        email = EmailMessage(subject, to=[to_email])
        email.template_id = 'labtrack_reset_password_template'
        email.merge_data = user_data
        email.send()


class CustomSetPasswordForm(SetPasswordForm):
    error_messages = {
        'password_mismatch': _('รหัสผ่านไม่ตรงกัน กรุณาลองใหม่อีกครั้ง'),
    }
