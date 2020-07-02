from django.urls import path
from django.views.generic.base import RedirectView

from . import views

app_name = "kmutnbtrackapp"

urlpatterns = [
    path('', views.home),
    path('signup/<str:lab_hash>/<str:tel_no>', views.signup_api, name='signup'), #
    path('api/usernamecheck/', views.username_check_api),
    path('login/', views.login_api, name="login"), # page+api
    path("logout/", views.logout_api, name="logout"), # api
    path('lab/', RedirectView.as_view(url="/", permanent=False)),
    path('lab/<str:lab_hash>/', views.lab_home_page, name='lab_home'),
    path('home/', views.home, name='home'),
    path('check_in/<str:lab_hash>/', views.check_in, name='check_in'),
    path('check_out/<str:lab_hash>/', views.check_out, name='check_out'),
    path('admin/clear/<str:lab_hash>/', views.view_lab, name='view_lab'),
]
