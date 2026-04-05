from django.db import models
from django.utils.translation import gettext_lazy as _

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True) # USD, EUR
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)
    exchange_rate_to_base = models.DecimalField(max_digits=18, decimal_places=6, default=1.0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} ({self.symbol})"

class CompanyProfileManager(models.Manager):
    def get_current(self):
        return self.first()

class CompanyProfile(models.Model):
    objects = CompanyProfileManager()

    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    logo = models.ImageField(upload_to="company_logos/", null=True, blank=True)
    fiscal_year_start_date = models.DateField()
    financial_year_end = models.DateField(null=True, blank=True)
    default_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    country_code = models.CharField(max_length=2, choices=[
        ('IE', 'Ireland'), ('GB', 'United Kingdom'), ('IN', 'India'), ('AE', 'UAE'),
    ], default='IE')
    state_code = models.CharField(max_length=5, blank=True, help_text="State/Province code for tax purposes")
    
    # VAT and Compliance
    vat_registered = models.BooleanField(default=False)
    vat_registration_number = models.CharField(max_length=20, blank=True)
    vat_services_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=42500)
    vat_goods_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=80000)
    
    # Banking
    bank_name = models.CharField(max_length=100, blank=True)
    iban = models.CharField(max_length=34, blank=True)

    def save(self, *args, **kwargs):
        if not self.financial_year_end and self.fiscal_year_start_date:
            from datetime import timedelta
            self.financial_year_end = self.fiscal_year_start_date + timedelta(days=364)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("company profile")
        verbose_name_plural = _("company profiles")
