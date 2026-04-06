from django.urls import path
from .reporting import views as reporting_views

app_name = 'accounting'

from .assets import views as asset_views

urlpatterns = [
    # Reporting
    path('reporting/profit-loss/', reporting_views.ProfitAndLossView.as_view(), name='profit_loss'),
    path('reporting/balance-sheet/', reporting_views.BalanceSheetView.as_view(), name='balance_sheet'),
    path('reporting/vat-summary/', reporting_views.VATSummaryView.as_view(), name='vat_summary'),
    path('reporting/bank-reconciliation/', reporting_views.BankReconciliationView.as_view(), name='bank_reconciliation'),
    path('reporting/bank-reconciliation/update/<int:pk>/', reporting_views.BankReconciliationUpdateView.as_view(), name='recon_update'),
    path('reporting/ct1/', reporting_views.CT1ComputationView.as_view(), name='ct1_list'),
    path('reporting/ct1/create/', reporting_views.CT1CreateView.as_view(), name='ct1_create'),
    
    # Statutory & Compliance
    path('reporting/statutory-registers/', reporting_views.StatutoryRegisterView.as_view(), name='statutory_registers'),
    path('reporting/dividends/', reporting_views.DividendListView.as_view(), name='dividend_list'),
    path('reporting/dividends/create/', reporting_views.DividendCreateView.as_view(), name='dividend_create'),
    path('reporting/related-parties/', reporting_views.RelatedPartyTransactionView.as_view(), name='related_party_list'),
    path('reporting/related-parties/create/', reporting_views.RelatedPartyTransactionCreateView.as_view(), name='related_party_create'),

    # Fixed Assets
    path('assets/', asset_views.FixedAssetListView.as_view(), name='asset_list'),
]
