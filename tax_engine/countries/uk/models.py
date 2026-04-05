from django.db import models
from django.core.validators import RegexValidator

class CompanyOfficer(models.Model):
    """Company director or secretary for Companies House"""
    OFFICER_ROLES = [
        ('director', 'Director'),
        ('secretary', 'Secretary'),
        ('llp_member', 'LLP Member'),
    ]
    
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE)
    
    # Personal details
    title = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    former_names = models.CharField(max_length=200, blank=True)
    
    # Identification
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=50)
    country_of_residence = models.CharField(max_length=50)
    
    # Service address (can be different from residential)
    service_address_line1 = models.CharField(max_length=100)
    service_address_line2 = models.CharField(max_length=100, blank=True)
    service_address_city = models.CharField(max_length=50)
    service_address_county = models.CharField(max_length=50, blank=True)
    service_address_country = models.CharField(max_length=50, default='United Kingdom')
    service_address_postcode = models.CharField(max_length=10)
    
    # Residential address (not public)
    residential_address_line1 = models.CharField(max_length=100)
    residential_address_line2 = models.CharField(max_length=100, blank=True)
    residential_address_city = models.CharField(max_length=50)
    residential_address_county = models.CharField(max_length=50, blank=True)
    residential_address_postcode = models.CharField(max_length=10)
    residential_address_country = models.CharField(max_length=50, default='United Kingdom')
    
    # Appointment
    role = models.CharField(max_length=20, choices=OFFICER_ROLES)
    appointment_date = models.DateField()
    resignation_date = models.DateField(null=True, blank=True)
    
    # Occupation (for directors)
    occupation = models.CharField(max_length=100, blank=True)
    
    # PSC (Person with Significant Control) flag
    is_psc = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['appointment_date']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.role}"
    
    @property
    def full_name(self):
        if self.title:
            return f"{self.title} {self.first_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

class ConfirmationStatement(models.Model):
    """CS01 Confirmation Statement filing"""
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE)
    
    statement_date = models.DateField()  # Made up to date
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Officers at date of statement
    current_officers = models.ManyToManyField(CompanyOfficer, related_name='+')
    
    # Share capital at date of statement
    ordinary_shares_authorised = models.PositiveIntegerField()
    ordinary_shares_issued = models.PositiveIntegerField()
    ordinary_share_nominal_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    preference_shares_authorised = models.PositiveIntegerField(null=True, blank=True)
    preference_shares_issued = models.PositiveIntegerField(null=True, blank=True)
    
    # PSC statements
    psc_statement = models.TextField(help_text="Statement of capital, rights attached to shares")
    
    # Trading status
    is_trading = models.BooleanField(default=True)
    sic_codes = models.CharField(max_length=200, help_text="SIC codes, comma separated")
    
    # Filing
    filing_number = models.CharField(max_length=50, unique=True, null=True)
    filed_at = models.DateTimeField(null=True)
    filed_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"CS01 - {self.period_end}"

class PersonWithSignificantControl(models.Model):
    """PSC (People with Significant Control) register"""
    NATURE_OF_CONTROL = [
        ('ownership', 'Ownership of shares >25%'),
        ('voting', 'Voting rights >25%'),
        ('board', 'Right to appoint/remove majority of board'),
        ('significant_influence', 'Significant influence or control'),
        ('trust', 'Trustee of trust with >25%'),
        ('firm', 'Member of firm with >25%'),
    ]
    
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE)
    
    # Individual or corporate
    is_corporate = models.BooleanField(default=False)
    
    # If individual
    title = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=50, blank=True)
    
    # If corporate
    corporate_name = models.CharField(max_length=200, blank=True)
    registration_number = models.CharField(max_length=50, blank=True)
    law_governed = models.CharField(max_length=100, blank=True)
    legal_form = models.CharField(max_length=100, blank=True)
    place_registered = models.CharField(max_length=100, blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    region = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    postcode = models.CharField(max_length=10)
    
    # Nature of control
    nature_of_control = models.CharField(max_length=50, choices=NATURE_OF_CONTROL)
    control_details = models.TextField(blank=True)
    
    # Shareholding (if applicable)
    shares_held = models.PositiveIntegerField(null=True, blank=True)
    percentage_held = models.DecimalField(max_digits=7, decimal_places=4, null=True)
    
    # Dates
    notified_date = models.DateField()
    ceased_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.is_corporate:
            return self.corporate_name
        return f"{self.first_name} {self.last_name}"
