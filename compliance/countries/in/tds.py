from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import User
from finance.models import JournalEntry, JournalEntryLine

class TDSSection(models.Model):
    """
    TDS (Tax Deducted at Source) Sections under Income Tax Act.
    E.g., 194C (Contractors), 194J (Professional Services)
    """
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='tds_sections')
    PARTY_TYPES = (
        ('company', _('Company')),
        ('non_company', _('Non-Company/Individual/HUF')),
    )

    section_code = models.CharField(max_length=10) # e.g., '194C'
    description = models.CharField(max_length=255)
    party_type = models.CharField(max_length=20, choices=PARTY_TYPES)
    rate_percent = models.DecimalField(max_digits=5, decimal_places=2)
    threshold_limit_single = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    threshold_limit_aggregate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Account to post TDS liability
    payable_account = models.ForeignKey('finance.Account', on_delete=models.PROTECT, related_name='tds_payable_sections')
    
    class Meta:
        verbose_name = _("TDS Section")
        verbose_name_plural = _("TDS Sections")
        unique_together = ['company', 'section_code', 'party_type']

    def __str__(self):
        return f"{self.section_code} ({self.get_party_type_display()}) - {self.rate_percent}%"


class TDSDeduction(models.Model):
    """
    Record of individual TDS deductions made on vendor bills.
    """
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='tds_deductions_in')
    bill = models.ForeignKey('finance.Invoice', on_delete=models.CASCADE, related_name='tds_deductions')
    vendor = models.ForeignKey('purchasing.Supplier', on_delete=models.CASCADE, related_name='tds_deductions')
    section = models.ForeignKey(TDSSection, on_delete=models.PROTECT)
    
    date_of_deduction = models.DateField()
    base_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Amount on which TDS is calculated")
    tds_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    journal_entry = models.OneToOneField(JournalEntry, on_delete=models.PROTECT, null=True, blank=True)
    
    challan = models.ForeignKey('TDSChallan', on_delete=models.SET_NULL, null=True, blank=True, related_name='deductions')
    
    class Meta:
        verbose_name = _("TDS Deduction")
        verbose_name_plural = _("TDS Deductions")

    def __str__(self):
        return f"TDS on {self.bill.invoice_number} under {self.section.section_code}"


class TDSChallan(models.Model):
    """
    Record of TDS payment deposited to the government (Challan 281).
    """
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='tds_challans_in')
    challan_number = models.CharField(max_length=20)
    bsr_code = models.CharField(max_length=7, help_text="7-digit BSR code of bank branch")
    date_of_deposit = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    journal_entry = models.OneToOneField(JournalEntry, on_delete=models.PROTECT, null=True, blank=True)
    
    class Meta:
        verbose_name = _("TDS Challan")
        verbose_name_plural = _("TDS Challans")

    def __str__(self):
        return f"Challan {self.challan_number} - {self.date_of_deposit}"


class TDSReturnQuarterly(models.Model):
    """
    Form 26Q (Non-Salary) / Form 24Q (Salary) quarterly returns.
    """
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='tds_returns_in')
    FORM_TYPES = (
        ('24q', _('Form 24Q (Salary)')),
        ('26q', _('Form 26Q (Other than Salary)')),
        ('27q', _('Form 27Q (Non-Resident)')),
    )
    QUARTERS = (
        ('q1', 'Q1 (Apr-Jun)'),
        ('q2', 'Q2 (Jul-Sep)'),
        ('q3', 'Q3 (Oct-Dec)'),
        ('q4', 'Q4 (Jan-Mar)'),
    )
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('generated', _('FVU Generated')),
        ('filed', _('Filed')),
    )

    financial_year = models.CharField(max_length=9) # e.g. "2023-2024"
    quarter = models.CharField(max_length=2, choices=QUARTERS)
    form_type = models.CharField(max_length=3, choices=FORM_TYPES)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    prn_number = models.CharField(max_length=50, blank=True, null=True, help_text="Provisional Receipt Number after filing")
    date_filed = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = _("TDS Quarterly Return")
        verbose_name_plural = _("TDS Quarterly Returns")
        unique_together = ['company', 'financial_year', 'quarter', 'form_type']

    def __str__(self):
        return f"Form {self.get_form_type_display()} - FY {self.financial_year} {self.get_quarter_display()}"
