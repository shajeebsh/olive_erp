from django.urls import path

from . import views

app_name = "finance"

urlpatterns = [
    path("invoices/", views.invoices, name="invoices"),
    path("invoices/create/", views.invoice_create, name="invoice_create"),
    path("invoices/<int:pk>/edit/", views.invoice_edit, name="invoice_edit"),
    path("invoices/<int:pk>/delete/", views.invoice_delete, name="invoice_delete"),
    path("expenses/", views.expenses, name="expenses"),
    path("journal/", views.journal, name="journal"),
    path("journal/create/", views.journal_create, name="journal_create"),
    path("accounts/", views.accounts, name="accounts"),
]
