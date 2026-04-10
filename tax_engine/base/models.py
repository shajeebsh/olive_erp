from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from datetime import date
import uuid

class CountryConfig(models.Model):
    """
    Base configuration for a country - extended by each country implementation
    """
    country_code = models.CharField(max_length=2, primary_key=True)
    country_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    # Tax configuration stored as JSON
    tax_config = models.JSONField(default=dict, help_text="""
    {
        "vat_rates": [
            {"rate": 23.0, "type": "standard", "description": "Standard Rate"},
            {"rate": 13.5, "type": "reduced", "description": "Reduced Rate"},
            {"rate": 0.0, "type": "zero", "description": "Zero Rate"}
        ],
        "tax_period": "monthly", # or quarterly, annual
        "currency": "EUR",
        "decimal_places": 2,
        "tax_number_pattern": "^IE\\d{7}[A-Z]?$",
        "tax_number_description": "11 characters: IE + 7 digits + optional letter"
    }
    """)

    # Statutory configuration
    statutory_config = models.JSONField(default=dict, help_text="""
    {
        "company_registry": "CRO",
        "annual_return_form": "B1",
        "filing_deadline": "28th February",
        "financial_year_end": "31-12",
        "forms": [
            {"code": "B1", "name": "Annual Return", "due_days": 56},
            {"code": "CT1", "name": "Corporation Tax", "due_days": 270}
        ]
    }
    """)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # This will be extended by concrete country models

    def clean(self):
        """Validate country-specific configuration"""
        if len(self.country_code) != 2:
            raise ValidationError("Country code must be 2 letters")

    def __str__(self):
        return f"{self.country_name} ({self.country_code})"


class TaxPeriod(models.Model):
    """
    Tax periods for a company (e.g., monthly VAT periods)
    """
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE)
    country = models.CharField(max_length=2, default='IE')  # References country_code

    period_type = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual')
    ])

    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date.today)
    due_date = models.DateField(default=date.today)

    status = models.CharField(max_length=20, choices=[
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('filed', 'Filed'),
        ('overdue', 'Overdue')
    ], default='open')

    # Tax calculation results (stored as JSON)
    tax_data = models.JSONField(null=True, blank=True)

    filed_at = models.DateTimeField(null=True, blank=True)
    filed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ['company', 'country', 'start_date']
        ordering = ['-end_date']

    def __str__(self):
        return f"{self.company.name} - {self.start_date} to {self.end_date}"

    def is_overdue(self):
        return date.today() > self.due_date and self.status != 'filed'


class TaxFiling(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    FILING_TYPES = [
        ("VAT3","VAT3 Return"),
        ("CT1","CT1 Corporation Tax"),
        ("CRO_B1","CRO B1 Annual Return"),
        ("RBO","RBO Beneficial Ownership"),
        ("PAYE","PAYE/PRSI"),
    ]
    STATUS = [
        ("draft","Draft"),
        ("pending","Pending Approval"),
        ("approved","Approved"),
        ("filed","Filed"),
        ("rejected","Rejected"),
    ]
    company = models.ForeignKey("company.CompanyProfile", on_delete=models.CASCADE)
    filing_type = models.CharField(max_length=20, choices=FILING_TYPES)
    period = models.CharField(max_length=20)          # e.g. "2024-Q2"
    due_date = models.DateField()
    filed_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="draft")
    reference = models.CharField(max_length=100, blank=True)
    data = models.JSONField(default=dict)              # Stores form field values
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.status not in ["filed"]

    @property
    def due_soon(self):
        from django.utils import timezone
        delta = self.due_date - timezone.now().date()
        return 0 <= delta.days <= 7 and self.status not in ["filed"]

    def __str__(self):
        return f"{self.get_filing_type_display()} - {self.period}"

class FilingApproval(models.Model):
    filing = models.OneToOneField(TaxFiling, on_delete=models.CASCADE)
    stage = models.CharField(max_length=20, choices=[
        ("prepare","Prepare"),
        ("cfo","CFO Review"),
        ("board","Board Approval"),
        ("filed","Filed"),
    ], default="prepare")
    cfo_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
        related_name="cfo_approvals", on_delete=models.SET_NULL)
    board_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
        related_name="board_approvals", on_delete=models.SET_NULL)
    filed_reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
