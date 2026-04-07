from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver, Signal
from django.core.cache import cache
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from datetime import date
from finance.models import JournalEntry, JournalEntryLine, Invoice
from apps.accounting.reconciliation.models import BankReconciliation
from company.models import CompanyProfile
from purchasing.models import PurchaseOrder
from inventory.models import Product


@receiver(user_logged_in)
def record_attendance_on_login(sender, request, user, **kwargs):
    """
    Record attendance when a user logs in.
    Replaces the brittle implementation in the auth backend.
    """
    try:
        from hr.models import Employee, Attendance
        # We need to handle the case where the user might not be an employee
        # or doesn't have an associated company in their profile yet.
        employee = Employee.objects.filter(user=user).select_related('company').first()
        if not employee:
            return

        today = date.today()
        # Ensure we don't create multiple attendance records for the same day
        # If the employee is already checked in, do nothing.
        if not Attendance.objects.filter(employee=employee, date=today).exists():
            Attendance.objects.create(
                company=employee.company,
                employee=employee,
                date=today,
                check_in_time=timezone.now().time()
            )
    except Exception as e:
        # We log the error instead of swallowing it silently,
        # but we don't block the login process if attendance fails.
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to record attendance for user {user.email}: {str(e)}")


# Custom signal for journal entry posted
journal_entry_posted = Signal()

@receiver(journal_entry_posted)
def handle_journal_entry_posted(sender, instance, **kwargs):
    """
    Handle logic when a journal entry is posted.
    """
    # JournalEntry doesn't have a direct company field. Get it from the lines.
    first_line = instance.lines.first()
    company = first_line.account.company if first_line else None
    
    if not company:
        company = CompanyProfile.objects.first()
        
    # 1. Invalidate P&L and Balance Sheet cache
    cache.delete(f"report_pl_{company.id}")
    cache.delete(f"report_bs_{company.id}")
    
    # 2. Mark ONLY the BankReconciliation for the specific month of the JE as 'IP' (In Progress)
    # Get the month/year of the journal entry
    je_year = instance.date.year
    je_month = instance.date.month
    
    # Find bank accounts affected by this journal entry
    affected_account_ids = instance.lines.values_list('account_id', flat=True)
    
    # Only invalidate the specific reconciliation period, not all future periods
    reconciliations = BankReconciliation.objects.filter(
        company=company,
        account_id__in=affected_account_ids,
        period_date__year=je_year,
        period_date__month=je_month
    )
    reconciliations.update(status='IP')
    
    # 3. Check VAT threshold (simplified placeholder)
    if company.vat_registered:
        from core.tasks import notify_vat_threshold
        notify_vat_threshold.delay(company.id)

@receiver(post_save, sender=JournalEntry)
def trigger_journal_entry_posted(sender, instance, created, **kwargs):
    if instance.is_posted:
        journal_entry_posted.send(sender=sender, instance=instance)


def log_audit(sender, instance, created, action=None, user=None):
    """Helper function to create audit log entries"""
    try:
        from .models import AuditLog
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Determine user - use instance's created_by/updated_by if available
        if not user:
            if hasattr(instance, 'created_by') and instance.created_by:
                user = instance.created_by
            elif hasattr(instance, 'updated_by') and instance.updated_by:
                user = instance.updated_by
            elif hasattr(instance, 'created_by'):
                # Try to get from request context (will need to be passed in)
                pass
        
        action_type = 'CREATE' if created else ('UPDATE' if action is None else action)
        
        # Build changes dict for updates
        changes = None
        if not created and hasattr(instance, '_state'):
            # For updates, we could track field changes - simplified for now
            pass
        
        AuditLog.objects.create(
            user=user,
            action=action_type,
            model_name=instance.__class__.__name__,
            object_id=str(instance.pk),
            object_repr=str(instance),
            changes=changes
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create audit log for {instance.__class__.__name__} {instance.pk}: {e}")


@receiver(post_save, sender=JournalEntry)
def audit_journal_entry(sender, instance, created, **kwargs):
    log_audit(sender, instance, created)


@receiver(pre_delete, sender=JournalEntry)
def audit_journal_entry_delete(sender, instance, **kwargs):
    log_audit(sender, instance, created=False, action='DELETE')


@receiver(post_save, sender=Invoice)
def audit_invoice(sender, instance, created, **kwargs):
    log_audit(sender, instance, created)


@receiver(pre_delete, sender=Invoice)
def audit_invoice_delete(sender, instance, **kwargs):
    log_audit(sender, instance, created=False, action='DELETE')


@receiver(post_save, sender=PurchaseOrder)
def audit_purchase_order(sender, instance, created, **kwargs):
    log_audit(sender, instance, created)


@receiver(pre_delete, sender=PurchaseOrder)
def audit_purchase_order_delete(sender, instance, **kwargs):
    log_audit(sender, instance, created=False, action='DELETE')


@receiver(post_save, sender=CompanyProfile)
def audit_company_profile(sender, instance, created, **kwargs):
    log_audit(sender, instance, created)


@receiver(pre_delete, sender=CompanyProfile)
def audit_company_profile_delete(sender, instance, **kwargs):
    log_audit(sender, instance, created=False, action='DELETE')


@receiver(post_save, sender=Product)
def audit_product(sender, instance, created, **kwargs):
    log_audit(sender, instance, created)


@receiver(pre_delete, sender=Product)
def audit_product_delete(sender, instance, **kwargs):
    log_audit(sender, instance, created=False, action='DELETE')
