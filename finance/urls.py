from django.urls import path

from . import views

app_name = "finance"

urlpatterns = [
    path("invoices/", views.invoices, name="invoices"),
    path("expenses/", views.expenses, name="expenses"),
    path("journal/", views.journal, name="journal"),
]
