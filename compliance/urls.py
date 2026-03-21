from django.urls import path
from compliance.views.dashboard import ComplianceDashboardView
from compliance.views.calendar import CalendarEventsView
from compliance.views.filing_history import FilingHistoryView, FilingDetailView
from compliance.views.approvals import ApprovalsView
from compliance.views.ie.vat3 import VAT3ReturnView
from compliance.views.ie.ct1 import CT1ReturnView
from compliance.views.ie.cro_b1 import CROB1View
from compliance.views.ie.rbo import RBOView
from compliance.views.ie.paye import PAYEView

from . import views, api

app_name = "compliance"

urlpatterns = [
    # Dashboard — FIX: was resolving to company wizard
    path("", ComplianceDashboardView.as_view(), name="dashboard"),

    # Calendar JSON endpoint
    path("calendar-events/", CalendarEventsView.as_view(), name="calendar_events"),

    # Filing history and approvals
    path("filings/", FilingHistoryView.as_view(), name="filing_history"),
    path("filings/<int:pk>/", FilingDetailView.as_view(), name="filing_detail"),
    path("approvals/", ApprovalsView.as_view(), name="approvals"),

    # Ireland-specific routes
    path("ie/vat3/", VAT3ReturnView.as_view(), name="ie_vat3"),
    path("ie/ct1/", CT1ReturnView.as_view(), name="ie_ct1"),
    path("ie/cro-b1/", CROB1View.as_view(), name="ie_cro_b1"),
    path("ie/rbo/", RBOView.as_view(), name="ie_rbo"),
    path("ie/paye/", PAYEView.as_view(), name="ie_paye"),
    
    # GB (UK) placeholders
    path('gb/ct600/', views.gb_ct600, name='gb_ct600'),
    path('gb/companies-house/', views.gb_companies_house, name='gb_companies_house'),
    path('gb/paye/', views.gb_paye, name='gb_paye'),
    
    # India placeholders
    path('in/gstr3b/', views.in_gstr3b, name='in_gstr3b'),
    path('in/gstr1/', views.in_gstr1, name='in_gstr1'),
    path('in/tds/', views.in_tds, name='in_tds'),
    path('in/eway/', views.in_eway, name='in_eway'),
    path('in/einvoice/', views.in_einvoice, name='in_einvoice'),
    
    # UAE placeholders
    path('ae/excise/', views.ae_excise, name='ae_excise'),
    path('ae/corporate-tax/', views.ae_corporate_tax, name='ae_corporate_tax'),
    path('ae/esr/', views.ae_esr, name='ae_esr'),

    # API endpoints
    path('api/deadlines/', api.ComplianceDeadlinesView.as_view(), name='api_deadlines'),
    path('api/deadlines/upcoming/', api.UpcomingDeadlinesView.as_view(), name='api_upcoming'),
    path('api/pending/', api.PendingFilingsView.as_view(), name='api_pending'),
]
