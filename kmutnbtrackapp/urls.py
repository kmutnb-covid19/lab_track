from django.urls import path

from . import views
from django.conf.urls import url
app_name="kmutnbtrackapp"

urlpatterns= [
    path('lab/<str:room_name>/', views.login, name='login'),
    path('home/',views.home, name='home'),
    path('check_in/<str:lab_name>/', views.checkIn, name='check_in'),
    path('check_out/<str:lab_name>/', views.checkOut, name='check_out'),
]