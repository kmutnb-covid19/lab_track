from django.urls import path
from django.contrib.auth.views import LoginView

from . import views

app_name = "kmutnbtrackapp"

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', LoginView.as_view(), name="login"),
    path('lab/<str:lab_hash>/', views.login_page, name='login'),
    path('home/', views.home, name='home'),
    path('check_in/<str:lab_hash>/', views.check_in, name='check_in'),

]
