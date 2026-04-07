from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from company.models import CompanyProfile
from finance.models import JournalEntryLine
from .compliance.models import ComplianceDeadline
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_deadline_reminders():
    """Notify users of upcoming compliance deadlines."""
    tomorrow = timezone.now().date() + timedelta(days=1)
    upcoming = ComplianceDeadline.objects.filter(deadline_date=tomorrow, status='PE')
    for deadline in upcoming:
        logger.info(f"REMINDER: {deadline.title} is due tomorrow!")

@shared_task
def notify_vat_threshold():
    """Check 12-month rolling income for VAT threshold limits."""
    companies = CompanyProfile.objects.all()
    twelve_months_ago = timezone.now().date() - timedelta(days=365)
    
    threshold_services = 42500
    threshold_goods = 82500
    
    for company in companies:
        total_income = JournalEntryLine.objects.filter(
            account__company=company,
            account__account_type='Income',
            journal_entry__date__gte=twelve_months_ago,
            journal_entry__is_posted=True
        ).aggregate(Sum('credit'))['credit__sum'] or 0
        
        if total_income > (threshold_services * 0.85):
            logger.warning(f"VAT WARNING: {company.name} is at {total_income/threshold_services*100:.1f}% of threshold.")
