from django.db import models
from django.core.validators import RegexValidator

class Director(models.Model):
    """Company director for CRO purposes"""
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE)
    
    # Personal details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    former_names = models.CharField(max_length=200, blank=True, help_text="Any former names")
    
    # Identification
    pps_number = models.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d{7}[A-Z]{1,2}$', 'Invalid PPS format')],
        blank=True
    )
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=50)
    
    # Address (must be physical, not PO box)
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    country = models.CharField(max_length=50, default='Ireland')
    country_code = models.CharField(max_length=2, default='IE')
    
    # Appointment details
    appointment_date = models.DateField()
    resignation_date = models.DateField(null=True, blank=True)
    
    # Director type
    is_executive = models.BooleanField(default=True)
    is_chairperson = models.BooleanField(default=False)
    
    # Other directorships (for disclosure)
    other_directorships = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['appointment_date']
        app_label = 'tax_engine'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_active(self):
        return self.resignation_date is None

class Secretary(models.Model):
    """Company secretary"""
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE)
    
    # Can be individual or corporate
    is_corporate = models.BooleanField(default=False)
    
    # If individual
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    
    # If corporate
    corporate_name = models.CharField(max_length=200, blank=True)
    registration_number = models.CharField(max_length=50, blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    country = models.CharField(max_length=50, default='Ireland')
    country_code = models.CharField(max_length=2, default='IE')
    
    appointment_date = models.DateField()
    resignation_date = models.DateField(null=True, blank=True)
    
    class Meta:
        app_label = 'tax_engine'
        
    def __str__(self):
        if self.is_corporate:
            return f"{self.corporate_name} (Corporate Secretary)"
        return f"{self.first_name} {self.last_name} (Secretary)"
    
    @property
    def is_active(self):
        return self.resignation_date is None
    
    @property
    def name(self):
        if self.is_corporate:
            return self.corporate_name
        return f"{self.first_name} {self.last_name}"

class ShareCapital(models.Model):
    """Company share capital structure"""
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE)
    
    class Meta:
        abstract = True
        app_label = 'tax_engine'

class OrdinaryShare(ShareCapital):
    """Ordinary shares"""
    currency = models.CharField(max_length=3, default='EUR')
    total_authorised = models.PositiveIntegerField(help_text="Total shares authorised")
    total_issued = models.PositiveIntegerField(help_text="Total shares issued")
    nominal_value = models.DecimalField(max_digits=10, decimal_places=2)
    paid_up_per_share = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        app_label = 'tax_engine'

    def total_nominal_value(self):
        return self.total_issued * self.nominal_value
    
    def total_paid_up(self):
        return self.total_issued * self.paid_up_per_share

class PreferenceShare(ShareCapital):
    """Preference shares"""
    currency = models.CharField(max_length=3, default='EUR')
    total_authorised = models.PositiveIntegerField()
    total_issued = models.PositiveIntegerField()
    nominal_value = models.DecimalField(max_digits=10, decimal_places=2)
    paid_up_per_share = models.DecimalField(max_digits=10, decimal_places=2)
    dividend_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Dividend percentage")
    
    class Meta:
        app_label = 'tax_engine'

    def total_nominal_value(self):
        return self.total_issued * self.nominal_value

class Shareholder(models.Model):
    """Individual or corporate shareholder"""
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE)
    
    # Can be individual or corporate
    is_corporate = models.BooleanField(default=False)
    
    # If individual
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    
    # If corporate
    corporate_name = models.CharField(max_length=200, blank=True)
    registration_number = models.CharField(max_length=50, blank=True)
    country_incorporation = models.CharField(max_length=50, blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    country_code = models.CharField(max_length=2, default='IE')
    
    # Shareholding
    ordinary_shares_held = models.PositiveIntegerField(default=0)
    preference_shares_held = models.PositiveIntegerField(default=0)
    percentage_held = models.DecimalField(max_digits=7, decimal_places=4, help_text="Percentage of total")
    
    date_joined = models.DateField()
    
    class Meta:
        app_label = 'tax_engine'

    def __str__(self):
        if self.is_corporate:
            return self.corporate_name
        return f"{self.first_name} {self.last_name}"
    
    @property
    def name(self):
        if self.is_corporate:
            return self.corporate_name
        return f"{self.first_name} {self.last_name}"
    
    @property
    def share_class(self):
        if self.preference_shares_held > 0:
            return "Preference"
        return "Ordinary"