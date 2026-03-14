from django.db import models
from django.shortcuts import render
from wagtail.models import Page
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from finance.models import Invoice, JournalEntry
from crm.models import SalesOrder
from inventory.models import StockLevel

class DashboardPage(Page):
    max_count = 1

    def get_context(self, request):
        context = super().get_context(request)
        if request.user.is_authenticated and request.user.is_employee:
            context['total_sales'] = sum(so.total_amount for so in SalesOrder.objects.filter(status='CONFIRMED'))
            context['pending_invoices'] = Invoice.objects.filter(status='DRAFT').count()
            context['low_stock_items'] = StockLevel.objects.filter(quantity_on_hand__lt=models.F('reorder_level'))
        return context

    @method_decorator(login_required)
    def serve(self, request):
        if not request.user.is_employee:
            return render(request, '403.html')
        return super().serve(request)
