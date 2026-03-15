from django.db import models
from django.utils.translation import gettext_lazy as _


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)  # USD, EUR
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)
    exchange_rate_to_base = models.DecimalField(
        max_digits=18, decimal_places=6, default=1.0
    )

    def __str__(self):
        return f"{self.code} ({self.symbol})"


class CompanyProfile(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    logo = models.ImageField(upload_to="company_logos/", null=True, blank=True)
    fiscal_year_start_date = models.DateField()
    default_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    country_code = models.CharField(
        max_length=2,
        choices=[
            ("IE", "Ireland"),
            ("GB", "United Kingdom"),
            ("IN", "India"),
            ("AE", "UAE"),
        ],
        default="IE",
        help_text="ISO Country Code",
    )
    state_code = models.CharField(
        max_length=5, blank=True, help_text="State/Province code for tax purposes"
    )

    @property
    def financial_year_end(self):
        """Calculate financial year end based on start date"""
        from datetime import date, timedelta

        # If fiscal year starts on Jan 1st, it ends on Dec 31st
        # We can calculate this by adding 1 year and subtracting 1 day
        try:
            # Handle leap years by replacing year and then subtracting
            end_date = self.fiscal_year_start_date.replace(
                year=self.fiscal_year_start_date.year + 1
            ) - timedelta(days=1)
            return end_date
        except ValueError:
            # Leap year edge case (Feb 29)
            return self.fiscal_year_start_date + timedelta(days=364)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("company profile")
        verbose_name_plural = _("company profiles")
