from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SalesOrder
from finance.models import Invoice
import datetime

@receiver(post_save, sender=SalesOrder)
def generate_invoice_on_confirmed(sender, instance, **kwargs):
    if instance.status == 'INVOICED':
        # Check if invoice already exists
        if not Invoice.objects.filter(invoice_number=f"INV-{instance.order_number}").exists():
            Invoice.objects.create(
                invoice_number=f"INV-{instance.order_number}",
                customer=instance.customer,
                issue_date=datetime.date.today(),
                due_date=datetime.date.today() + datetime.timedelta(days=30),
                total_amount=instance.total_amount,
                status='DRAFT'
            )
