from celery import shared_task
from django.core.mail import send_mail
from finance.models import Invoice
from inventory.models import Product, StockLevel
import datetime

@shared_task
def send_invoice_reminders():
    overdue_invoices = Invoice.objects.filter(status='OVERDUE', due_date__lt=datetime.date.today())
    for invoice in overdue_invoices:
        send_mail(
            'Payment Reminder',
            f'Your invoice {invoice.invoice_number} is overdue.',
            'billing@wagtailerp.com',
            [invoice.customer.email],
            fail_silently=True,
        )

@shared_task
def update_inventory_valuations():
    # Example logic for nightly valuation
    total_value = sum(
        sl.quantity_on_hand * sl.product.cost_price 
        for sl in StockLevel.objects.all()
    )
    # Log or save valuation to a model
    print(f"Total Inventory Value: {total_value}")
