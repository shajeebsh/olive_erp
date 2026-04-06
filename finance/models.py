from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from company.models import CompanyProfile, Currency

class Account(models.Model):
    ACCOUNT_TYPES = [
        ('Asset', 'Asset'),
        ('Liability', 'Liability'),
        ('Equity', 'Equity'),
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    ]
    
    GROUP_TYPE_CHOICES = [
        ('Primary', 'Primary'),
        ('Sub-group', 'Sub-group'),
        ('Ledger', 'Ledger'),
    ]
    
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='Asset')
    group_type = models.CharField(max_length=20, choices=GROUP_TYPE_CHOICES, default='Ledger')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                               related_name='children')
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    opening_balance_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        unique_together = ['code', 'company']
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_balance(self, as_on_date=None):
        """Calculate account balance as on date using journal entries"""
        from django.db.models import Sum
        from datetime import date
        
        if not as_on_date:
            as_on_date = date.today()
        
        # Sum all debit/credit up to the date
        lines = JournalEntryLine.objects.filter(
            account=self,
            journal_entry__date__lte=as_on_date,
            journal_entry__is_posted=True
        )
        
        total_debit = lines.aggregate(Sum('debit'))['debit__sum'] or 0
        total_credit = lines.aggregate(Sum('credit'))['credit__sum'] or 0
        
        # For Asset/Expense accounts: Debit increases balance
        if self.account_type in ['Asset', 'Expense']:
            return self.opening_balance + total_debit - total_credit
        # For Liability/Equity/Income accounts: Credit increases balance
        else:
            return self.opening_balance + total_credit - total_debit
    
    def get_hierarchy_path(self):
        """Return full path like 'Assets:Current Assets:Cash'"""
        if self.parent:
            return f"{self.parent.get_hierarchy_path()}:{self.name}"
        return self.name

class JournalEntry(models.Model):
    entry_number = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    is_posted = models.BooleanField(default=False)

    def __str__(self):
        return self.entry_number

class JournalEntryLine(models.Model):
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    debit = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    cost_centre = models.ForeignKey('CostCentre', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    
    # New fields for enhancements
    payment_method = models.CharField(max_length=50, blank=True)
    invoice_number = models.CharField(max_length=50, blank=True)
    is_related_party = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.journal_entry.entry_number} - {self.account.name}"

class Invoice(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    )
    invoice_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey('crm.Customer', on_delete=models.PROTECT)
    invoice_template = models.ForeignKey('InvoiceTemplate', on_delete=models.SET_NULL, null=True, blank=True)
    issue_date = models.DateField()
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=18, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Missing fields for tracking
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='invoices', null=True)
    type = models.CharField(max_length=10, choices=(('sales', 'Sales'), ('purchase', 'Purchase')), default='sales')
    supplier = models.ForeignKey('purchasing.Supplier', on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_invoices')
    
    # GST components for India
    cgst_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    sgst_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    igst_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    utgst_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    def __str__(self):
        return self.invoice_number

    def recalculate_totals(self):
        """Recompute total_amount and tax_amount from line items."""
        from django.db.models import Sum
        agg = self.items.aggregate(
            subtotal=Sum('line_total'),
            tax=Sum('tax_amount'),
        )
        self.total_amount = (agg['subtotal'] or 0) + (agg['tax'] or 0)
        self.tax_amount = agg['tax'] or 0
        self.save(update_fields=['total_amount', 'tax_amount'])


class InvoiceItem(models.Model):
    """Line items for an Invoice — supports price lists & discounts."""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    product = models.ForeignKey('inventory.Product', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=4, default=1)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                   help_text="Tax percentage, e.g. 15 for 15%")
    # Computed
    line_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    notes = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        taxable = (self.quantity * self.unit_price) - self.discount_amount
        self.tax_amount = taxable * (self.tax_rate / 100)
        self.line_total = taxable
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice.invoice_number} — {self.description}"


class CostCentre(models.Model):
    """For profit/cost centre accounting - tracks profitability by department/project"""
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='children')
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['code', 'company']
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_hierarchy_path(self):
        if self.parent:
            return f"{self.parent.get_hierarchy_path()}:{self.name}"
        return self.name
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.code and self.company_id:
            existing = CostCentre.objects.filter(code=self.code, company_id=self.company_id)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({'code': f'A cost centre with code "{self.code}" already exists for this company.'})


class CostCentreAllocation(models.Model):
    """Allocate journal entry lines to cost centres"""
    journal_entry_line = models.ForeignKey(JournalEntryLine, on_delete=models.CASCADE,
                                           related_name='cost_allocations')
    cost_centre = models.ForeignKey(CostCentre, on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)  # 0-100%
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    def save(self, *args, **kwargs):
        if self.percentage:
            self.amount = (self.journal_entry_line.debit + self.journal_entry_line.credit) * self.percentage / 100
        super().save(*args, **kwargs)


class Budget(models.Model):
    PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    name = models.CharField(max_length=100)
    financial_year = models.CharField(max_length=9)  # e.g., "2025-26"
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    cost_centre = models.ForeignKey(CostCentre, on_delete=models.CASCADE, 
                                     null=True, blank=True)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    budget_amount = models.DecimalField(max_digits=15, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['financial_year', 'account', 'cost_centre', 'period']
    
    @property
    def variance(self):
        return self.budget_amount - self.actual_amount
    
    @property
    def variance_percentage(self):
        if self.budget_amount:
            return (self.variance / self.budget_amount) * 100
        return 0
    
    def update_actual(self):
        """Calculate actual amount from journal entries"""
        from django.db.models import Sum
        from datetime import date
        
        start_year = int(self.financial_year[:4])
        if self.company.fiscal_year_start_date:
            fy_start = self.company.fiscal_year_start_date
        else:
            fy_start = date(start_year, 4, 1)
        
        fy_end = date(start_year + 1, 3, 31)
        
        lines = JournalEntryLine.objects.filter(
            account=self.account,
            journal_entry__date__range=[fy_start, fy_end],
            journal_entry__is_posted=True
        )
        
        if self.cost_centre:
            lines = lines.filter(cost_centre=self.cost_centre)
        
        if self.account.account_type in ['Expense']:
            self.actual_amount = lines.aggregate(Sum('debit'))['debit__sum'] or 0
        else:
            self.actual_amount = lines.aggregate(Sum('credit'))['credit__sum'] or 0
        
        self.save()


class BillWiseDetail(models.Model):
    """Track outstanding amounts by bill/invoice"""
    BILL_TYPES = [
        ('sales', 'Sales Invoice'),
        ('purchase', 'Purchase Invoice'),
        ('payment', 'Payment'),
        ('receipt', 'Receipt'),
    ]
    
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE)
    reference_type = models.CharField(max_length=20, choices=BILL_TYPES)
    reference_number = models.CharField(max_length=50)
    reference_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    outstanding_amount = models.DecimalField(max_digits=15, decimal_places=2)
    due_date = models.DateField()
    party_name = models.CharField(max_length=200)
    is_fully_settled = models.BooleanField(default=False)
    
    def update_outstanding(self):
        """Calculate outstanding after payments/receipts"""
        from django.db.models import Sum
        
        if self.reference_type in ['sales', 'receipt']:
            payments = BillWiseDetail.objects.filter(
                reference_type='payment',
                reference_number=self.reference_number
            )
            paid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        else:
            receipts = BillWiseDetail.objects.filter(
                reference_type='receipt',
                reference_number=self.reference_number
            )
            paid = receipts.aggregate(Sum('amount'))['amount__sum'] or 0
        
        self.outstanding_amount = self.amount - paid
        self.is_fully_settled = self.outstanding_amount <= 0
        self.save()


class PaymentAllocation(models.Model):
    """Link payments/receipts to specific bills"""
    payment_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE,
                                      related_name='allocations')
    bill_detail = models.ForeignKey(BillWiseDetail, on_delete=models.CASCADE)
    allocated_amount = models.DecimalField(max_digits=15, decimal_places=2)
    allocation_date = models.DateField(auto_now_add=True)


class InvoiceTemplate(models.Model):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    is_default = models.BooleanField(default=False)
    template_html = models.TextField(help_text="HTML template with placeholders")
    template_css = models.TextField(blank=True, help_text="Custom CSS for PDF")
    
    logo_position = models.CharField(max_length=20, choices=[
        ('top-left', 'Top Left'),
        ('top-center', 'Top Center'),
        ('top-right', 'Top Right'),
    ], default='top-left')
    
    show_tax_breakup = models.BooleanField(default=True)
    show_discount = models.BooleanField(default=True)
    show_terms = models.BooleanField(default=True)
    show_bank_details = models.BooleanField(default=False)
    
    footer_text = models.TextField(blank=True)
    terms_text = models.TextField(blank=True, default="1. Goods once sold will not be taken back.\n2. Interest @ 24% p.a. will be charged on overdue payments.")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['name', 'company']
    
    def save(self, *args, **kwargs):
        if self.is_default:
            InvoiceTemplate.objects.filter(company=self.company, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class PriceList(models.Model):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    customer_group = models.ForeignKey('crm.CustomerGroup', on_delete=models.SET_NULL,
                                       null=True, blank=True)
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-priority', 'name']


class PriceListItem(models.Model):
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    min_quantity = models.PositiveIntegerField(default=1)


class DiscountRule(models.Model):
    DISCOUNT_TYPES = [('percentage', 'Percentage'), ('fixed', 'Fixed Amount')]
    name = models.CharField(max_length=100)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    customer_group = models.ForeignKey('crm.CustomerGroup', on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey('crm.Customer', on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey('inventory.Product', on_delete=models.SET_NULL, null=True, blank=True)
    product_category = models.ForeignKey('inventory.Category', on_delete=models.SET_NULL, null=True, blank=True)
    min_quantity = models.PositiveIntegerField(default=1)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)


class RecurringInvoice(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'), ('yearly', 'Yearly'),
    ]
    name = models.CharField(max_length=200)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    customer = models.ForeignKey('crm.Customer', on_delete=models.CASCADE)
    invoice_template = models.ForeignKey(InvoiceTemplate, on_delete=models.SET_NULL, null=True)
    items = models.JSONField()
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    interval = models.PositiveIntegerField(default=1)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    next_invoice_date = models.DateField()
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CreditDebitNote(models.Model):
    NOTE_TYPES = [('credit', 'Credit Note'), ('debit', 'Debit Note')]
    note_number = models.CharField(max_length=50, unique=True)
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    original_invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='credit_notes')
    date = models.DateField()
    reason = models.TextField()
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class SystemConfig(models.Model):
    """Global system configurations (F11/F12 logic)"""
    company = models.OneToOneField(CompanyProfile, on_delete=models.CASCADE, related_name='config')
    
    # Financial Settings
    base_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    fiscal_year_start = models.DateField(default="2025-04-01")
    
    # Feature Toggles
    enable_cost_centres = models.BooleanField(default=True)
    enable_budgets = models.BooleanField(default=True)
    enable_billwise_details = models.BooleanField(default=True)
    enable_multi_currency = models.BooleanField(default=False)
    
    # Module Settings
    invoice_prefix = models.CharField(max_length=10, default="INV-")
    stock_valuation_method = models.CharField(max_length=20, choices=[
        ('fifo', 'FIFO'),
        ('lifo', 'LIFO'),
        ('avco', 'Average Cost')
    ], default='fifo')
    
    # Notification & Audit
    enable_audit_trail = models.BooleanField(default=True)
    alert_on_overdue = models.BooleanField(default=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Config for {self.company.company_name}"
