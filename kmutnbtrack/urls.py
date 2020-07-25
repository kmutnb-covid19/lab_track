"""kmutnbtrack URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from kmutnbtrackapp import views

urlpatterns = [
    path('', include('kmutnbtrackapp.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('privacy/', TemplateView.as_view(template_name="Page/privacy.html"), name='privacy_policy'),
    path('admin/kmutnbtrackapp/lab/qrcode/<str:lab_hash>/', views.generate_qr_code, name='generate_qr_code'),
    path('admin/kmutnbtrackapp/lab/view/<str:lab_hash>/', views.view_lab, name='view_lab'),
    path('admin/dashboard/', views.call_dashboard, name='dashboard'),
    path('admin/history/search/riskpeople/', views.risk_people_search, name='risk_people_search'),
    path('admin/history/search/riskpeople/<int:page>', views.risk_people_search),
    path('admin/history/search/riskpeople/notify_confirm/<str:where>', views.notify_confirm, name='notify_confirm'),
    url(r'^admin/history/search/riskpeople/notify/(?P<mode>.+)/(?P<keyword>.+)/$', views.notify_user, name='notify'),
    path('admin/history/search/riskpeople/download_risk_csv/', views.export_risk_csv, name='download_risk_csv'),
    path('admin/history/search/history/', RedirectView.as_view(url='/admin/history/search/history/1/', permanent=False),
         name='history_search'),
    path('admin/history/search/history/<int:page>/', views.history_search, name="history_search_function"),
    path('admin/history/search/history/download_normal_csv/', views.export_normal_csv, name='download_normal_csv'),
    path('admin/backup', views.backup, name='backup'),
    path('admin/', admin.site.urls, name='admin'),
    path('staff_signup/', views.staff_signup, name="staff_signup"),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]
