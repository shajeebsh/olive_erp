from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('finance/', views.finance_dashboard, name='finance_dashboard'),
    path('inventory/', views.inventory_dashboard, name='inventory_dashboard'),
    path('hr/', views.hr_dashboard, name='hr_dashboard'),
    path('crm/', views.crm_dashboard, name='crm_dashboard'),
    path('projects/', views.projects_dashboard, name='projects_dashboard'),
    path('reporting/', views.reporting_dashboard, name='reporting_dashboard'),
    path('compliance/', views.compliance_dashboard, name='compliance_dashboard'),
]
