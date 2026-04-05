"""
Corporate Tax (Federal Decree-Law No. 47 of 2022)
"""
from django.db import models
from django.conf import settings
from decimal import Decimal

class CorporateTaxReturn(models.Model):
    """
    Corporate Tax return for a tax period
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('filed', 'Filed'),
        ('amended', 'Amended'),
    ]
    
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE)
    
    tax_period_start = models.DateField()
    tax_period_end = models.DateField()
    
    # Financials
    revenue = models.DecimalField(max_digits=15, decimal_places=2)
    cost_of_goods_sold = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gross_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    operating_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    other_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    other_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    net_profit_before_tax = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Adjustments
    non_deductible_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    exempt_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    reliefs = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    losses_brought_forward = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    taxable_income = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Tax calculation
    small_business_relief = models.BooleanField(default=False)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Free Zone person (qualifying income)
    is_free_zone_person = models.BooleanField(default=False)
    qualifying_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    non_qualifying_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Filing
    filing_date = models.DateField(null=True)
    filing_reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    created_at = models.DateTimeField(auto_now_add=True)
    filed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        unique_together = ['company', 'tax_period_start', 'tax_period_end']
        ordering = ['-tax_period_end']
    
    def __str__(self):
        return f"CT Return - {self.tax_period_start.year}"

class TaxLoss(models.Model):
    """
    Tax losses carried forward
    """
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE)
    
    loss_year = models.IntegerField()
    loss_amount = models.DecimalField(max_digits=15, decimal_places=2)
    utilized_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Losses can be carried forward indefinitely (as per UAE CT law)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Loss {self.loss_year} - AED {self.loss_amount}"

class FreeZonePerson(models.Model):
    """
    Qualifying Free Zone Person details
    """
    FREE_ZONE_CHOICES = [
        ('dubai_airport', 'Dubai Airport Freezone (DAFZ)'),
        ('jafza', 'Jebel Ali Free Zone (JAFZA)'),
        ('dmcc', 'Dubai Multi Commodities Centre (DMCC)'),
        ('dubai_south', 'Dubai South'),
        ('dwc', 'Dubai World Central'),
        ('rakftz', 'Ras Al Khaimah Free Trade Zone'),
        ('shams', 'Hamriyah Free Zone'),
        ('saif', 'Sharjah Airport International Free Zone'),
        ('ajman_ftz', 'Ajman Free Zone'),
        ('other', 'Other Free Zone'),
    ]
    
    company = models.OneToOneField('company.CompanyProfile', on_delete=models.CASCADE)
    
    free_zone_name = models.CharField(max_length=50, choices=FREE_ZONE_CHOICES)
    free_zone_license_no = models.CharField(max_length=100)
    license_issue_date = models.DateField()
    license_expiry_date = models.DateField()
    
    # Qualifying income activities
    has_qualifying_activities = models.BooleanField(default=True)
    qualifying_activities_description = models.TextField()
    
    # De minimis threshold (non-qualifying revenue < 5% or AED 5M)
    non_qualifying_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.company.name} - {self.get_free_zone_name_display()}"
    
    def check_de_minimis(self, total_revenue):
        """Check if non-qualifying revenue is within de minimis limits"""
        if self.non_qualifying_revenue == 0:
            return True
        
        percent = (self.non_qualifying_revenue / total_revenue * 100) if total_revenue > 0 else 0
        
        # De minimis: lower of 5% of revenue or AED 5,000,000
        return (percent <= 5) or (self.non_qualifying_revenue <= 5000000)
