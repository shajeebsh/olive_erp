"""
Excise Tax management for UAE
As per Federal Decree-Law No. (7) of 2017 on Excise Tax
"""
from django.db import models
from django.conf import settings
from decimal import Decimal

class ExciseGoodsCategory(models.Model):
    """
    Categories of goods subject to Excise Tax
    """
    EXCISE_TYPES = [
        ('tobacco', 'Tobacco Products'),
        ('energy_drinks', 'Energy Drinks'),
        ('carbonated', 'Carbonated Drinks'),
        ('sweetened', 'Sweetened Drinks'),
        ('electronic_smoking', 'Electronic Smoking Devices'),
        ('liquids', 'Liquids for Electronic Smoking'),
    ]
    
    name = models.CharField(max_length=50, choices=EXCISE_TYPES, unique=True)
    display_name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2)  # percentage
    description = models.TextField()
    
    # UAE Customs tariff codes (HS codes) applicable
    customs_tariff_codes = models.TextField(help_text="Comma-separated HS codes")
    
    # Effective dates
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    
    # Special conditions
    requires_marking = models.BooleanField(default=False, help_text="Digital tax stamps required")
    marking_scheme = models.CharField(max_length=50, blank=True, help_text="e.g., 'DTS' for Digital Tax Stamps")
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Excise goods categories"
    
    def __str__(self):
        return f"{self.display_name} - {self.rate}%"

class ExciseProduct(models.Model):
    """
    Specific products subject to Excise Tax
    """
    category = models.ForeignKey(ExciseGoodsCategory, on_delete=models.CASCADE)
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    
    # Override rate if different from category
    override_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # For products requiring digital tax stamps
    has_digital_stamp = models.BooleanField(default=False)
    stamp_identifier = models.CharField(max_length=100, blank=True)
    
    # Excise warehouse details
    is_in_excise_warehouse = models.BooleanField(default=False)
    warehouse_approval_number = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.category.display_name}"
    
    @property
    def effective_rate(self):
        return self.override_rate or self.category.rate

class ExciseDeclaration(models.Model):
    """
    Excise Tax declaration (monthly)
    """
    DECLARATION_TYPES = [
        ('import', 'Import'),
        ('manufacture', 'Manufacture'),
        ('release', 'Release from warehouse'),
    ]
    
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE)
    
    declaration_type = models.CharField(max_length=20, choices=DECLARATION_TYPES)
    declaration_period = models.DateField()  # First day of month
    
    # Total excise due
    total_excise_due = models.DecimalField(max_digits=15, decimal_places=2)
    total_quantity = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Payment details
    payment_due_date = models.DateField()
    payment_made = models.BooleanField(default=False)
    payment_date = models.DateField(null=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    # Filing
    filed_at = models.DateTimeField(null=True)
    filed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-declaration_period']
    
    def __str__(self):
        return f"Excise Declaration - {self.declaration_period.strftime('%B %Y')}"

class ExciseDeclarationLine(models.Model):
    """
    Line items in Excise declaration
    """
    declaration = models.ForeignKey(ExciseDeclaration, on_delete=models.CASCADE, related_name='lines')
    
    category = models.ForeignKey(ExciseGoodsCategory, on_delete=models.CASCADE)
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    
    quantity = models.DecimalField(max_digits=15, decimal_places=2)
    unit = models.CharField(max_length=20)
    
    retail_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_retail_value = models.DecimalField(max_digits=15, decimal_places=2)
    
    excise_rate = models.DecimalField(max_digits=5, decimal_places=2)
    excise_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.unit}"
