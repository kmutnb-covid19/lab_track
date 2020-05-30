from django.urls import path

from . import views
from django.conf.urls import url
app_name="kmutnbtrackapp"
urlpatterns= [
    path('room/<str:room_name>/', views.login, name='login'),
    path('home/',views.home, name='home'),
    path('check_in/',views.checkIn, name='check_in'),
]