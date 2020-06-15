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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from kmutnbtrackapp import views    

urlpatterns = [
    path('', include('kmutnbtrackapp.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('qr_code/', include('qr_code.urls', namespace="qr_code")),
    path('admin/qrcode/', views.generate_qr_code, name='generate_qr_code'),
    path('admin/dashboard/', views.call_dashboard, name='dashboard'),
    path('admin/history/search/', TemplateView.as_view(template_name="admin/history_search_main.html"),
         name='admin_search'),
    path('admin/history/search/riskpeople/', views.risk_people_search, name='risk_people_search'),
    path('admin/history/search/riskpeople/<int:page>', views.risk_people_search),
    path('admin/history/search/riskpeople/notify/', views.notify_user, name='notify'),
    path('admin/history/search/riskpeople/download_risk_csv/', views.export_risk_csv, name='download_risk_csv'),
    path('admin/history/search/history/', views.history_search, name='history_search'),
    path('admin/history/search/history/<int:page>', views.history_search),
    path('admin/history/search/history/download_normal_csv/', views.export_normal_csv, name='download_normal_csv'),
    path('admin/', admin.site.urls),
    
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
urlpatterns += staticfiles_urlpatterns()