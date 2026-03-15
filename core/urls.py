from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('goto-search/', views.GoToSearchView.as_view(), name='goto_search'),
    path('audit/', views.audit_log, name='audit_log'),
    path('system-config/', views.system_config, name='system_config'),
]
