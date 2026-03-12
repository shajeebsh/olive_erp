import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from company.models import CompanyProfile
from finance.models import Account, JournalEntry


class TaxPeriod(models.Model):
    """
    Represents a tax period for compliance reporting.
    """

    class PeriodType(models.TextChoices):
        MONTHLY = "MONTHLY", _("Monthly")
        QUARTERLY = "QUARTERLY", _("Quarterly")
        ANNUAL = "ANNUAL", _("Annual")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    period_type = models.CharField(
        _("period type"), max_length=20, choices=PeriodType.choices
    )

    # Period dates
    start_date = models.DateField(_("start date"))
    end_date = models.DateField(_("end date"))

    # Status
    is_closed = models.BooleanField(_("is closed"), default=False)
    closed_at = models.DateTimeField(_("closed at"), null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Tax Period")
        verbose_name_plural = _("Tax Periods")
        ordering = ["-start_date"]
        unique_together = ["company", "start_date", "end_date"]

    def __str__(self):
        return f"{self.company.name} - {self.start_date} to {self.end_date}"


class Filing(models.Model):
    """
    Represents a compliance filing for a specific tax period.
    """

    class FilingType(models.TextChoices):
        VAT = "VAT", _("VAT Return")
        CT = "CT", _("Corporation Tax")
        CRO = "CRO", _("CRO Annual Return")
        RBO = "RBO", _("RBO Beneficial Ownership")
        PAYE = "PAYE", _("PAYE/PRSI")
        FINANCIAL_STATEMENTS = "FINANCIAL_STATEMENTS", _("Financial Statements")

    class FilingStatus(models.TextChoices):
        DRAFT = "DRAFT", _("Draft")
        PENDING_APPROVAL = "PENDING_APPROVAL", _("Pending Approval")
        APPROVED = "APPROVED", _("Approved")
        FILED = "FILED", _("Filed")
        REJECTED = "REJECTED", _("Rejected")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    tax_period = models.ForeignKey(TaxPeriod, on_delete=models.CASCADE)

    filing_type = models.CharField(
        _("filing type"), max_length=20, choices=FilingType.choices
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=FilingStatus.choices,
        default=FilingStatus.DRAFT,
    )

    # Filing details
    filing_reference = models.CharField(
        _("filing reference"), max_length=100, blank=True
    )
    filing_date = models.DateField(_("filing date"), null=True, blank=True)
    due_date = models.DateField(_("due date"))

    # Financial data
    amount_due = models.DecimalField(
        _("amount due"), max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    amount_paid = models.DecimalField(
        _("amount paid"), max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    payment_date = models.DateField(_("payment date"), null=True, blank=True)

    # Document storage
    generated_document = models.FileField(
        _("generated document"),
        upload_to="compliance/documents/%Y/%m/%d/",
        null=True,
        blank=True,
    )
    filed_document = models.FileField(
        _("filed document"),
        upload_to="compliance/filed/%Y/%m/%d/",
        null=True,
        blank=True,
    )

    # Approval workflow
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_filings",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_filings",
    )
    filed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="filed_filings",
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Filing")
        verbose_name_plural = _("Filings")
        ordering = ["-due_date"]
        unique_together = ["company", "tax_period", "filing_type"]

    def __str__(self):
        return f"{self.get_filing_type_display()} - {self.tax_period}"


class FinancialStatement(models.Model):
    """
    Financial statements for compliance and reporting.
    """

    class StatementType(models.TextChoices):
        BALANCE_SHEET = "BALANCE_SHEET", _("Balance Sheet")
        PROFIT_LOSS = "PROFIT_LOSS", _("Profit & Loss")
        CASH_FLOW = "CASH_FLOW", _("Cash Flow Statement")
        NOTES = "NOTES", _("Notes to Accounts")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    tax_period = models.ForeignKey(TaxPeriod, on_delete=models.CASCADE)

    statement_type = models.CharField(
        _("statement type"), max_length=20, choices=StatementType.choices
    )

    # Statement data
    statement_data = models.JSONField(_("statement data"), default=dict)
    is_approved = models.BooleanField(_("is approved"), default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    approved_at = models.DateTimeField(_("approved at"), null=True, blank=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Financial Statement")
        verbose_name_plural = _("Financial Statements")
        ordering = ["-tax_period__end_date", "statement_type"]

    def __str__(self):
        return f"{self.get_statement_type_display()} - {self.tax_period}"


class BeneficialOwner(models.Model):
    """
    Beneficial ownership information for RBO reporting.
    """

    class OwnerType(models.TextChoices):
        INDIVIDUAL = "INDIVIDUAL", _("Individual")
        COMPANY = "COMPANY", _("Company")
        TRUST = "TRUST", _("Trust")
        OTHER = "OTHER", _("Other")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)

    owner_type = models.CharField(
        _("owner type"), max_length=20, choices=OwnerType.choices
    )

    # Owner details
    name = models.CharField(_("name"), max_length=255)
    address = models.TextField(_("address"))
    nationality = models.CharField(_("nationality"), max_length=100, blank=True)
