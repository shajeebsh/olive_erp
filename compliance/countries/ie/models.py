from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from company.models import CompanyProfile
from compliance.models import Filing, TaxPeriod
import uuid
from decimal import Decimal


class IrelandVATReturn(models.Model):
    """
    Ireland-specific VAT Return (VAT3) data and calculations.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filing = models.OneToOneField(Filing, on_delete=models.CASCADE, related_name='ireland_vat_return')
    
    # VAT Calculation Fields
    vat_on_sales = models.DecimalField(_("VAT on Sales"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    vat_on_purchases = models.DecimalField(_("VAT on Purchases"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    vat_on_imports = models.DecimalField(_("VAT on Imports"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # VAT Rates (Ireland specific)
    standard_rate = models.DecimalField(_("Standard Rate"), max_digits=4, decimal_places=2, default=Decimal('23.00'))
    reduced_rate = models.DecimalField(_("Reduced Rate"), max_digits=4, decimal_places=2, default=Decimal('13.50'))
    second_reduced_rate = models.DecimalField(_("Second Reduced Rate"), max_digits=4, decimal_places=2, default=Decimal('9.00'))
    
    # VAT Calculation Results
    total_vat_due = models.DecimalField(_("Total VAT Due"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_vat_reclaimable = models.DecimalField(_("Total VAT Reclaimable"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    net_vat_payable = models.DecimalField(_("Net VAT Payable"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # VAT Period Information
    vat_period = models.CharField(_("VAT Period"), max_length=10)  # e.g., "2023-Q4"
    vat_number = models.CharField(_("VAT Number"), max_length=20)
    
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    
    class Meta:
        verbose_name = _("Ireland VAT Return")
        verbose_name_plural = _("Ireland VAT Returns")
    
    def __str__(self):
        return f"VAT Return - {self.vat_period} - {self.filing.company.name}"


class IrelandCTReturn(models.Model):
    """
    Ireland-specific Corporation Tax Return (CT1) data and calculations.
    """
    
    class AccountingPeriod(models.TextChoices):
        STANDARD = 'STANDARD', _('Standard 12 Months')
        SHORT = 'SHORT', _('Short Accounting Period')
        LONG = 'LONG', _('Long Accounting Period')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filing = models.OneToOneField(Filing, on_delete=models.CASCADE, related_name='ireland_ct_return')
    
    # CT Calculation Fields
    accounting_period = models.CharField(_("Accounting Period"), max_length=20, choices=AccountingPeriod.choices)
    
    # Income Calculations
    trading_income = models.DecimalField(_("Trading Income"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    rental_income = models.DecimalField(_("Rental Income"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    investment_income = models.DecimalField(_("Investment Income"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    other_income = models.DecimalField(_("Other Income"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Deductions and Allowances
    capital_allowances = models.DecimalField(_("Capital Allowances"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    losses_forward = models.DecimalField(_("Losses Forward"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    rnd_credits = models.DecimalField(_("R&D Credits"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Tax Calculation
    taxable_profit = models.DecimalField(_("Taxable Profit"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    ct_rate = models.DecimalField(_("CT Rate"), max_digits=4, decimal_places=2, default=Decimal('12.50'))
    ct_liability = models.DecimalField(_("CT Liability"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Payment Information
    preliminary_tax_paid = models.DecimalField(_("Preliminary Tax Paid"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    balance_due = models.DecimalField(_("Balance Due"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Company Information
    ct_number = models.CharField(_("CT Number"), max_length=20)
    accounting_period_end = models.DateField(_("Accounting Period End"))
    
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    
    class Meta:
        verbose_name = _("Ireland CT Return")
        verbose_name_plural = _("Ireland CT Returns")
    
    def __str__(self):
        return f"CT Return - {self.accounting_period_end} - {self.filing.company.name}"


class IrelandCROReturn(models.Model):
    """
    Ireland-specific CRO Annual Return (Form B1) data.
    """
    
    class CompanyType(models.TextChoices):
        LTD = 'LTD', _('Private Company Limited by Shares')
        DAC = 'DAC', _('Designated Activity Company')
        PLC = 'PLC', _('Public Limited Company')
        ULC = 'ULC', _('Unlimited Company')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filing = models.OneToOneField(Filing, on_delete=models.CASCADE, related_name='ireland_cro_return')
    
    # Company Information
    company_type = models.CharField(_("Company Type"), max_length=10, choices=CompanyType.choices)
    cro_number = models.CharField(_("CRO Number"), max_length=20)
    registered_office = models.TextField(_("Registered Office"))
    
    # Share Capital Information
    authorized_share_capital = models.DecimalField(_("Authorized Share Capital"), max_digits=15, decimal_places=2, default=Decimal('0.00'))
    issued_share_capital = models.DecimalField(_("Issued Share Capital"), max_digits=15, decimal_places=2, default=Decimal('0.00'))
    number_of_shares = models.IntegerField(_("Number of Shares"), default=0)
    
    # Director Information
    number_of_directors = models.IntegerField(_("Number of Directors"), default=0)
    director_details = models.JSONField(_("Director Details"), default=list)
    
    # Secretary Information
    has_company_secretary = models.BooleanField(_("Has Company Secretary"), default=False)
    secretary_details = models.JSONField(_("Secretary Details"), default=dict)
    
    # Financial Information
    annual_return_date = models.DateField(_("Annual Return Date"))
    financial_statements_attached = models.BooleanField(_("Financial Statements Attached"), default=False)
    
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    
    class Meta:
        verbose_name = _("Ireland CRO Return")
        verbose_name_plural = _("Ireland CRO Returns")
    
    def __str__(self):
        return f"CRO Return - {self.annual_return_date} - {self.filing.company.name}"


class IrelandRBOFiling(models.Model):
    """
    Ireland-specific RBO (Register of Beneficial Ownership) filing data.
    """
    
    class FilingType(models.TextChoices):
        INITIAL = 'INITIAL', _('Initial Filing')
        UPDATE = 'UPDATE', _('Update Filing')
        CORRECTION = 'CORRECTION', _('Correction Filing')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filing = models.OneToOneField(Filing, on_delete=models.CASCADE, related_name='ireland_rbo_filing')
    
    # RBO Filing Information
    filing_type = models.CharField(_("Filing Type"), max_length=20, choices=FilingType.choices)
    rbo_number = models.CharField(_("RBO Number"), max_length=30)
    
    # Beneficial Ownership Details
    beneficial_owners = models.JSONField(_("Beneficial Owners"), default=list)
    total_percentage_owned = models.DecimalField(_("Total Percentage Owned"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Contact Information
    presenter_name = models.CharField(_("Presenter Name"), max_length=255)
    presenter_email = models.EmailField(_("Presenter Email"))
    presenter_phone = models.CharField(_("Presenter Phone"), max_length=20)
    
    # Filing Status
    rbo_confirmation_number = models.CharField(_("RBO Confirmation Number"), max_length=50, blank=True)
    filing_date = models.DateField(_("Filing Date"), null=True, blank=True)
    
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    
    class Meta:
        verbose_name = _("Ireland RBO Filing")
        verbose_name_plural = _("Ireland RBO Filings")
    
    def __str__(self):
        return f"RBO Filing - {self.get_filing_type_display()} - {self.filing.company.name}"


class IrelandPAYEReturn(models.Model):
    """
    Ireland-specific PAYE Modernization return data.
    """
    
    class ReturnPeriod(models.TextChoices):
        MONTHLY = 'MONTHLY', _('Monthly')
        QUARTERLY = 'QUARTERLY', _('Quarterly')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filing = models.OneToOneField(Filing, on_delete=models.CASCADE, related_name='ireland_paye_return')
    
    # PAYE Return Information
    return_period = models.CharField(_("Return Period"), max_length=20, choices=ReturnPeriod.choices)
    period_start = models.DateField(_("Period Start"))
    period_end = models.DateField(_("Period End"))
    
    # Employee Information
    number_of_employees = models.IntegerField(_("Number of Employees"), default=0)
    total_gross_pay = models.DecimalField(_("Total Gross Pay"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Tax Calculations
    total_paye_deducted = models.DecimalField(_("Total PAYE Deducted"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_prsi_deducted = models.DecimalField(_("Total PRSI Deducted"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_usc_deducted = models.DecimalField(_("Total USC Deducted"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Payment Information
    total_payment_due = models.DecimalField(_("Total Payment Due"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    payment_made = models.BooleanField(_("Payment Made"), default=False)
    payment_date = models.DateField(_("Payment Date"), null=True, blank=True)
    
    # Revenue Information
    ros_number = models.CharField(_("ROS Number"), max_length=20)
    employer_reg_number = models.CharField(_("Employer Reg Number"), max_length=20)
    
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    
    class Meta:
        verbose_name = _("Ireland PAYE Return")
        verbose_name_plural = _("Ireland PAYE Returns")
    
    def __str__(self):
        return f"PAYE Return - {self.period_end} - {self.filing.company.name}"