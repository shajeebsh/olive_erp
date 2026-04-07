from celery import shared_task
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from finance.models import Invoice
from inventory.models import Product, StockLevel
import datetime
import logging

logger = logging.getLogger(__name__)

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
    from django.db.models import Sum
    total_value = StockLevel.objects.aggregate(
        total=Sum(models.F('quantity_on_hand') * models.F('product__cost_price'))
    )['total'] or 0
    logger = logging.getLogger(__name__)
    logger.info(f"Total Inventory Value: {total_value}")

@shared_task
def send_deadline_reminders():
    from apps.accounting.compliance.models import ComplianceDeadline
    from django.utils import timezone
    
    upcoming = ComplianceDeadline.objects.filter(
        deadline_date__lte=timezone.now().date() + datetime.timedelta(days=7),
        status='PE'
    )
    for deadline in upcoming:
        send_mail(
            'Compliance Reminder',
            f'Deadline for {deadline.title} is on {deadline.deadline_date}.',
            'compliance@wagtailerp.com',
            [deadline.responsible_party or 'admin@wagtailerp.com'],
            fail_silently=True,
        )

@shared_task
def notify_vat_threshold(company_id):
    from company.models import CompanyProfile
    from django.db.models import Sum
    from finance.models import JournalEntryLine
    
    company = CompanyProfile.objects.get(id=company_id)
    # Simple check: sum all sales (Credit) for current year
    sales = JournalEntryLine.objects.filter(
        journal_entry__company=company,
        account__account_type='Income',
        journal_entry__date__year=datetime.date.today().year
    ).aggregate(total=Sum('credit'))['total'] or 0
    
    if sales >= company.vat_services_threshold:
        send_mail(
            'VAT Threshold Alert',
            f'Sales of {sales} have reached or exceeded the threshold of {company.vat_services_threshold}.',
            'compliance@wagtailerp.com',
            [company.email],
            fail_silently=True,
        )
