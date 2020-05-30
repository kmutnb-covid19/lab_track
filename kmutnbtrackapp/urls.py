from django.urls import path

from . import views
from django.conf.urls import url
app_name="kmutnbtrackapp"
urlpatterns= [
    path('', views.login, name='login'),
]