"""
Imports should be grouped in the following order:

1.Standard library imports.
2.Related third party imports.
3.Local application/library specific imports.
"""

from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, INTERNAL_RESET_SESSION_TOKEN
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from kmutnbtrackapp.models import *


class CustomPasswordResetView(PasswordResetView):
    def post(self, request, *args, **kwargs):
        self.extra_email_context = {
            'lab_hash': self.request.POST['lab_hash']
        }
        return super().post(request, *args, **kwargs)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('password_reset_complete')

    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])
        lab_hash = self.request.GET.get('next')
        self.success_url = reverse_lazy('password_reset_complete', kwargs={'next': lab_hash})

        if self.user is not None:
            print(lab_hash)
            token = kwargs['token']
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, self.reset_url_token) + "?next=" + lab_hash
                    return HttpResponseRedirect(redirect_url)
        return self.render_to_response(self.get_context_data())


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    def get_context_data(self, **kwargs):
        assert 'next' in kwargs
        self.extra_context = {
            'lab_hash_receive': kwargs['next'],
            'lab_name': Lab.objects.get(hash=kwargs['next']).name
        }
        return super().get_context_data(**kwargs)
