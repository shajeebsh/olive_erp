from django.db import models
from django.utils.translation import gettext_lazy as _

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True) # USD, EUR
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)
    exchange_rate_to_base = models.DecimalField(max_digits=18, decimal_places=6, default=1.0)

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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("company profile")
        verbose_name_plural = _("company profiles")
