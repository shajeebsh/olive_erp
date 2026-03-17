from django.urls import path

from . import views, api

app_name = "compliance"

urlpatterns = [
    path('cro-b1/', views.cro_b1, name='cro_b1'),
    path('ct1/', views.ct1, name='ct1'),
    path('vat/', views.vat, name='vat'),
    path('rbo/', views.rbo, name='rbo'),
    path('paye/', views.paye, name='paye'),
    
    # GB (UK)
    path('gb/ct600/', views.gb_ct600, name='gb_ct600'),
    path('gb/companies-house/', views.gb_companies_house, name='gb_companies_house'),
    path('gb/paye/', views.gb_paye, name='gb_paye'),
    
    # India
    path('in/gstr3b/', views.in_gstr3b, name='in_gstr3b'),
    path('in/gstr1/', views.in_gstr1, name='in_gstr1'),
    path('in/tds/', views.in_tds, name='in_tds'),
    path('in/eway/', views.in_eway, name='in_eway'),
    path('in/einvoice/', views.in_einvoice, name='in_einvoice'),
    
    # UAE
    path('ae/excise/', views.ae_excise, name='ae_excise'),
    path('ae/corporate-tax/', views.ae_corporate_tax, name='ae_corporate_tax'),
    path('ae/esr/', views.ae_esr, name='ae_esr'),
    
    path('calendar/', views.calendar, name='calendar'),
    path('history/', views.history, name='history'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('return_preview/', views.return_preview, name='return_preview'),
    path('return_preview/<int:return_id>/', views.return_preview, name='return_preview_id'),
    path('approval/', views.approval_workflow, name='approval_workflow'),
    
    # API endpoints
    path('api/deadlines/', api.ComplianceDeadlinesView.as_view(), name='api_deadlines'),
    path('api/deadlines/upcoming/', api.UpcomingDeadlinesView.as_view(), name='api_upcoming'),
    path('api/pending/', api.PendingFilingsView.as_view(), name='api_pending'),
]
