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
