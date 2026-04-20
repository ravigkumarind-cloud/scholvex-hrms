from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('admin/', admin.site.urls),

    # ALL WEBSITE + MODULES
    path('', include('accounts.urls')),

    path('employees/', include('employees.urls')),

    # WEBSITE PAGES
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),

    # DASHBOARDS
    path('chairman/', views.chairman_dashboard, name='chairman_dashboard'),
    path('md/', views.md_dashboard, name='md_dashboard'),
    path('director/', views.director_dashboard, name='director_dashboard'),
    path('hod/', views.hod_dashboard, name='hod_dashboard'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('marketing/', views.marketing_dashboard, name='marketing_dashboard'),
    path('sales/', views.sales_dashboard, name='sales_dashboard'),
    path('tl/', views.tl_dashboard, name='tl_dashboard'),
    path('hr/', views.hr_dashboard, name='hr_dashboard'),
    path('accounts-dashboard/', views.accounts_dashboard, name='accounts_dashboard'),
    path('partner/', views.partner_dashboard, name='partner_dashboard'),
    path('security/', views.security_dashboard, name='security_dashboard'),
    path('technical/', views.technical_dashboard, name='technical_dashboard'),
    path('legal/', views.legal_dashboard, name='legal_dashboard'),
    path('bpo/', views.bpo_dashboard, name='bpo_dashboard'),
    path('production/', views.production_dashboard, name='production_dashboard'),
    path('pro/', views.pro_dashboard, name='pro_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # APPS
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

