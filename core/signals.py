from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django.core.cache import cache
from finance.models import JournalEntry, JournalEntryLine
from apps.accounting.reconciliation.models import BankReconciliation
from company.models import CompanyProfile

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
    
    # 2. Mark BankReconciliation for affected month as 'IP' (In Progress)
    reconciliations = BankReconciliation.objects.filter(
        company=company,
        account__in=instance.lines.values_list('account', flat=True),
        period_date__gte=instance.date
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
