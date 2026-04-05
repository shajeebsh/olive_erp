from django.db import models
from company.models import CompanyProfile

class ComplianceDeadline(models.Model):
    STATUS_CHOICES = [
        ('PE', 'Pending'),
        ('CO', 'Completed'),
        ('FI', 'Filed'),
        ('OV', 'Overdue'),
    ]
    
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    deadline_date = models.DateField()
    responsible_party = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='PE')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.deadline_date}"

class ChecklistItem(models.Model):
    deadline = models.ForeignKey(ComplianceDeadline, on_delete=models.CASCADE, related_name='checklist_items')
    task = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

class CT1Computation(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    period_start = models.DateField()
    period_end = models.DateField()
    
    net_profit_per_accounts = models.DecimalField(max_digits=15, decimal_places=2)
    add_back_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    less_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    taxable_profit = models.DecimalField(max_digits=15, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=12.5)
    tax_payable = models.DecimalField(max_digits=15, decimal_places=2)
    
    is_finalized = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CT1 {self.company.name} {self.period_end}"

class Dividend(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    shareholder_name = models.CharField(max_length=200)
    declaration_date = models.DateField()
    payment_date = models.DateField()
    
    dividend_per_share = models.DecimalField(max_digits=10, decimal_places=4)
    number_of_shares = models.PositiveIntegerField()
    net_amount = models.DecimalField(max_digits=15, decimal_places=2)
    tax_credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    voucher_number = models.CharField(max_length=50, unique=True)
    is_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Div {self.voucher_number} - {self.shareholder_name}"

class RelatedPartyTransaction(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    party_name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=200, help_text="e.g. Director, Parent Company")
    
    transaction_date = models.DateField()
    transaction_nature = models.TextField(help_text="e.g. Loan, Management Fees, Rent")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    is_arm_length = models.BooleanField(default=True, help_text="Was the transaction at market value?")
    disclosure_required = models.BooleanField(default=True)
    
    def __str__(self):
        return f"RPT {self.party_name} - {self.amount}"
