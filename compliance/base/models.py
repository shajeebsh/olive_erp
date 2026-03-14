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
    """
    Record of actual tax filings submitted
    """
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    tax_period = models.ForeignKey(TaxPeriod, on_delete=models.CASCADE)
    filing_type = models.CharField(max_length=50)  # e.g., 'VAT3', 'GSTR-1'

    filing_data = models.JSONField()  # Data that was filed
    response_data = models.JSONField(null=True, blank=True)  # Response from tax authority

    submitted_at = models.DateTimeField(auto_now_add=True)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    # For electronic filing
    acknowledgment_no = models.CharField(max_length=100, blank=True)
    filing_status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], default='draft')

    def __str__(self):
        return f"{self.filing_type} - {self.tax_period}"
