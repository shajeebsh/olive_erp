from django.db import models
from django.conf import settings
from company.models import CompanyProfile
from finance.models import Account, JournalEntryLine

class BankReconciliation(models.Model):
    STATUS_CHOICES = [
        ('NS', 'Not Started'),
        ('IP', 'In Progress'),
        ('RC', '✅ Reconciled'),
        ('DC', '⚠️ Discrepancy'),
    ]
    
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='reconciliations')
    
    period_date = models.DateField(help_text="The last date of the reconciliation month")
    
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    actual_closing_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    statement_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0) # Kept for backward compat
    book_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='NS')
    reconciled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['account', 'period_date']
        ordering = ['period_date']

    def __str__(self):
        return f"{self.account.name} - {self.period_date}"

    @property
    def month_label(self):
        return self.period_date.strftime('%B %Y')

    @property
    def period_display(self):
        import calendar
        last_day = calendar.monthrange(self.period_date.year, self.period_date.month)[1]
        return f"01 - {last_day} {self.period_date.strftime('%b %y')}"

    @property
    def period_income(self):
        return JournalEntryLine.objects.filter(
            account=self.account,
            journal_entry__date__year=self.period_date.year,
            journal_entry__date__month=self.period_date.month,
            credit__gt=0
        ).aggregate(models.Sum('credit'))['credit__sum'] or 0

    @property
    def period_expenses(self):
        return JournalEntryLine.objects.filter(
            account=self.account,
            journal_entry__date__year=self.period_date.year,
            journal_entry__date__month=self.period_date.month,
            debit__gt=0
        ).aggregate(models.Sum('debit'))['debit__sum'] or 0

    @property
    def expected_closing(self):
        return self.opening_balance + self.period_income - self.period_expenses

    @property
    def difference(self):
        if self.actual_closing_balance is None:
            return None
        return self.actual_closing_balance - self.expected_closing
