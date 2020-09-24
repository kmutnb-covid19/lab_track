from django.urls import path
from django.views.generic.base import RedirectView

from . import views

app_name = "kmutnbtrackapp"

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/<str:lab_hash>/', views.signup_api, name='signup'),
    path('login/', views.login_api, name="login"),
    path("logout/", views.logout_api, name="logout"),
    path('lab/', RedirectView.as_view(url="/", permanent=False)),
    path('lab/<str:lab_hash>/', views.lab_home_page, name='lab_home'),
    path('home/', views.home, name='home'),
    path('check_in/<str:lab_hash>/', views.check_in, name='check_in'),
    path('check_out/<str:lab_hash>/', views.check_out, name='check_out'),
    path('api/addfeedback/', views.add_feedback_api, name='add_feedback')
]
