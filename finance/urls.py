from django.urls import path

from . import views

app_name = "finance"

urlpatterns = [
    # Invoices
    path("invoices/", views.InvoiceListView.as_view(), name="invoices"),
    path("invoices/create/", views.InvoiceCreateView.as_view(), name="invoice_create"),
    path("invoices/<int:pk>/edit/", views.InvoiceUpdateView.as_view(), name="invoice_edit"),
    path("invoices/<int:pk>/delete/", views.InvoiceDeleteView.as_view(), name="invoice_delete"),
    
    # Expenses & Journal
    path("expenses/", views.ExpenseListView.as_view(), name="expenses"),
    path("journal/", views.JournalEntryListView.as_view(), name="journal"),
    path("journal/create/", views.JournalEntryCreateView.as_view(), name="journal_create"),
    
    # Accounts (CBVs)
    path("accounts/", views.AccountListView.as_view(), name="account_list"),
    path("accounts/create/", views.AccountCreateView.as_view(), name="account_create"),
    path("accounts/<int:pk>/", views.AccountDetailView.as_view(), name="account_detail"),
    path("accounts/<int:pk>/update/", views.AccountUpdateView.as_view(), name="account_update"),
    
    # Cost Centres
    path("cost-centres/", views.CostCentreListView.as_view(), name="costcentre_list"),
    path("cost-centres/create/", views.CostCentreCreateView.as_view(), name="costcentre_create"),
    
    # Budgets
    path("budgets/", views.BudgetListView.as_view(), name="budget_list"),
    path("budgets/create/", views.BudgetCreateView.as_view(), name="budget_create"),

    # Price Lists & Discount Rules
    path("price-lists/", views.PriceListView.as_view(), name="pricelist_list"),
    path("price-lists/create/", views.PriceListCreateView.as_view(), name="pricelist_create"),
    path("discount-rules/", views.DiscountRuleListView.as_view(), name="discountrule_list"),
    path("discount-rules/create/", views.DiscountRuleCreateView.as_view(), name="discountrule_create"),

    # Recurring Invoices
    path("recurring-invoices/", views.RecurringInvoiceListView.as_view(), name="recurring_invoice_list"),
    path("recurring-invoices/create/", views.RecurringInvoiceCreateView.as_view(), name="recurring_invoice_create"),

    # Credit/Debit Notes
    path("notes/", views.CreditDebitNoteListView.as_view(), name="note_list"),
    path("notes/create/", views.CreditDebitNoteCreateView.as_view(), name="note_create"),

    # Invoice Templates
    path("templates/", views.InvoiceTemplateListView.as_view(), name="template_list"),

    # System Configuration
    path("config/", views.SystemConfigUpdateView.as_view(), name="system_config"),
]
