from django.urls import path
from django.contrib.auth.views import LoginView
from django.views.generic.base import RedirectView

from . import views

app_name = "kmutnbtrackapp"

urlpatterns = [
    path('', views.home),
    path('signup/', views.signup, name='signup'), #
    path('login/', LoginView.as_view(), name="login"), # page+api
    path("logout/", views.logout_api, name="logout"), # api
    path('lab/', RedirectView.as_view(url="/", permanent=False)),
    path('lab/<str:lab_hash>/', views.lab_home_page, name='lab_home'),
    path('home/', views.home, name='home'),
    path('check_in/<str:lab_hash>/', views.check_in, name='check_in'),

]
