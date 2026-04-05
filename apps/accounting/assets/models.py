from decimal import Decimal
from django.db import models
from django.conf import settings
from company.models import CompanyProfile
from finance.models import Account, JournalEntry, JournalEntryLine

class FixedAsset(models.Model):
    DEPRECIATION_METHODS = [
        ('SL', 'Straight Line'),
        ('RB', 'Reducing Balance'),
    ]
    
    name = models.CharField(max_length=200)
    asset_code = models.CharField(max_length=50, unique=True)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    asset_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='fixed_assets')
    accumulated_depreciation_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='fixed_assets_accumulated')
    depreciation_expense_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='fixed_assets_expense')
    
    purchase_date = models.DateField()
    purchase_value = models.DecimalField(max_digits=15, decimal_places=2)
    salvage_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    depreciation_method = models.CharField(max_length=2, choices=DEPRECIATION_METHODS, default='SL')
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Annual rate in percentage")
    
    accumulated_depreciation = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    last_depreciation_date = models.DateField(null=True, blank=True)
    
    is_disposed = models.BooleanField(default=False)
    disposal_date = models.DateField(null=True, blank=True)
    disposal_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asset_code} - {self.name}"

    @property
    def net_book_value(self):
        return self.purchase_value - self.accumulated_depreciation

    @property
    def years_held(self):
        from datetime import date
        delta = date.today() - self.purchase_date
        return round(delta.days / 365.25, 2)

    def calculate_current_depreciation(self):
        """
        Calculate total depreciation from purchase_date to today based on method.
        """
        if self.is_disposed:
            return self.accumulated_depreciation
        
        years = self.years_held
        if self.depreciation_method == 'SL':
            # Straight Line: (Cost - Salvage) * Rate * Years
            total = (self.purchase_value - self.salvage_value) * (self.depreciation_rate / 100) * Decimal(str(years))
            return min(total, self.purchase_value - self.salvage_value)
        elif self.depreciation_method == 'RB':
            # Reducing Balance: Cost * (1 - Rate)^Years
            rate = self.depreciation_rate / 100
            nbv = self.purchase_value * (Decimal(str(1 - float(rate))) ** Decimal(str(years)))
            return self.purchase_value - nbv
        return 0

    def run_depreciation_entry(self):
        """
        Create JournalEntry for depreciation and update accumulated_depreciation.
        """
        # Logic to create JEs...
        pass

    class Meta:
        ordering = ['asset_code']
