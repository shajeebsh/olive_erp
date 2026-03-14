"""
Celery tasks for automatic recurring invoice generation (Feature 6).
Run with: celery -A wagtailerp worker -l info
Schedule with: celery -A wagtailerp beat -l info
"""
from celery import shared_task
from django.utils import timezone
from dateutil.relativedelta import relativedelta


@shared_task(name='finance.generate_recurring_invoices')
def generate_recurring_invoices():
    """
    Daily task that checks all active RecurringInvoice records and generates
    new Invoice instances when next_invoice_date <= today.
    """
    from finance.models import RecurringInvoice, Invoice, InvoiceItem

    today = timezone.now().date()
    generated_count = 0

    active_schedules = RecurringInvoice.objects.filter(
        is_active=True,
        next_invoice_date__lte=today
    ).select_related('customer', 'invoice_template', 'company')

    for schedule in active_schedules:
        # Check end date
        if schedule.end_date and today > schedule.end_date:
            schedule.is_active = False
            schedule.save(update_fields=['is_active'])
            continue

        # Generate a sequential invoice number
        prefix = getattr(schedule.company, 'config', None)
        invoice_prefix = prefix.invoice_prefix if prefix else 'INV-'
        count = Invoice.objects.filter(customer=schedule.customer).count() + 1
        invoice_number = f"{invoice_prefix}{count:05d}"

        # Create the invoice
        invoice = Invoice.objects.create(
            invoice_number=invoice_number,
            customer=schedule.customer,
            invoice_template=schedule.invoice_template,
            issue_date=today,
            due_date=today + relativedelta(days=30),
            total_amount=schedule.total_amount,
            tax_amount=schedule.tax_amount,
            status='SENT',
        )

        # Clone line items from schedule if any
        for item_data in schedule.items or []:
            InvoiceItem.objects.create(
                invoice=invoice,
                description=item_data.get('description', ''),
                quantity=item_data.get('quantity', 1),
                unit_price=item_data.get('unit_price', 0),
                tax_rate=item_data.get('tax_rate', 0),
            )

        # Advance next_invoice_date
        freq = schedule.frequency
        interval = schedule.interval or 1
        if freq == 'daily':
            schedule.next_invoice_date += relativedelta(days=interval)
        elif freq == 'weekly':
            schedule.next_invoice_date += relativedelta(weeks=interval)
        elif freq == 'monthly':
            schedule.next_invoice_date += relativedelta(months=interval)
        elif freq == 'quarterly':
            schedule.next_invoice_date += relativedelta(months=3 * interval)
        elif freq == 'annually':
            schedule.next_invoice_date += relativedelta(years=interval)

        schedule.save(update_fields=['next_invoice_date'])
        generated_count += 1

    return f"Generated {generated_count} recurring invoices on {today}"
