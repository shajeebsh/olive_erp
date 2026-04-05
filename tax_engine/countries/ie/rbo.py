from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings

class BeneficialOwner(models.Model):
    """Register of Beneficial Ownership (RBO)"""
    INTEREST_TYPES = [
        ('direct', 'Direct Ownership'),
        ('indirect', 'Indirect Ownership'),
        ('voting', 'Voting Rights'),
        ('control', 'Control via other means'),
    ]
    
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE)
    
    # Personal details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    former_names = models.CharField(max_length=200, blank=True)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=50)
    pps_number = models.CharField(max_length=9, blank=True)
    
    # Residential address (must be physical)
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    country = models.CharField(max_length=50, default='Ireland')
    country_code = models.CharField(max_length=2, default='IE')
    
    # Nature of beneficial interest
    interest_type = models.CharField(max_length=20, choices=INTEREST_TYPES)
    interest_details = models.TextField(help_text="Describe the nature of interest")
    
    # Shareholding percentage (if applicable)
    shares_held = models.PositiveIntegerField(null=True, blank=True)
    percentage_held = models.DecimalField(max_digits=7, decimal_places=4, null=True)
    
    # Voting rights percentage (if applicable)
    voting_rights_percentage = models.DecimalField(max_digits=7, decimal_places=4, null=True)
    
    # Dates
    became_owner_date = models.DateField()
    ceased_owner_date = models.DateField(null=True, blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, related_name='verified_owners')
    verified_at = models.DateTimeField(null=True)
    
    # Supporting documents (uploaded files)
    identification_document = models.FileField(upload_to='rbo/id/', null=True)
    proof_of_address = models.FileField(upload_to='rbo/address/', null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-percentage_held']
        unique_together = ['company', 'first_name', 'last_name', 'date_of_birth']
        app_label = 'tax_engine'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.percentage_held}%"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class RBORegistration(models.Model):
    """Record of RBO filings with the Central Register"""
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE)
    
    registration_number = models.CharField(max_length=50, unique=True)
    filing_date = models.DateField(auto_now_add=True)
    
    # Beneficial owners at time of filing
    owners_included = models.ManyToManyField(BeneficialOwner)
    
    # Filing status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted to RBO'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Response from RBO
    response_data = models.JSONField(null=True)
    rejection_reason = models.TextField(blank=True)
    
    filed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True)
    
    class Meta:
        ordering = ['-filing_date']
        app_label = 'tax_engine'
    
    def __str__(self):
        return f"RBO Filing {self.registration_number} - {self.filing_date}"

class RBOUpload(models.Model):
    """Generate RBO XML for upload"""
    
    class Meta:
        app_label = 'tax_engine'

    @staticmethod
    def generate_xml(company, owners):
        """Generate RBO XML format for upload"""
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom import minidom
        
        root = Element('RBOFiling')
        root.set('xmlns', 'http://www.rbo.gov.ie/schema')
        
        # Company details
        company_elem = SubElement(root, 'Company')
        SubElement(company_elem, 'Name').text = company.name
        SubElement(company_elem, 'CRONumber').text = company.registration_number
        
        # Beneficial owners
        owners_elem = SubElement(root, 'BeneficialOwners')
        
        for owner in owners:
            owner_elem = SubElement(owners_elem, 'BeneficialOwner')
            SubElement(owner_elem, 'FirstName').text = owner.first_name
            SubElement(owner_elem, 'LastName').text = owner.last_name
            SubElement(owner_elem, 'DateOfBirth').text = owner.date_of_birth.isoformat()
            SubElement(owner_elem, 'Nationality').text = owner.nationality
            
            # Address
            addr = SubElement(owner_elem, 'ResidentialAddress')
            SubElement(addr, 'Line1').text = owner.address_line1
            SubElement(addr, 'City').text = owner.city
            SubElement(addr, 'County').text = owner.county
            SubElement(addr, 'Country').text = owner.country
            
            # Interest
            interest = SubElement(owner_elem, 'NatureOfInterest')
            SubElement(interest, 'Type').text = owner.interest_type
            SubElement(interest, 'Details').text = owner.interest_details
            
            if owner.percentage_held:
                SubElement(interest, 'PercentageHeld').text = str(owner.percentage_held)
            
            if owner.voting_rights_percentage:
                SubElement(interest, 'VotingRightsPercentage').text = str(owner.voting_rights_percentage)
        
        # Pretty print
        xml_str = minidom.parseString(tostring(root)).toprettyxml(indent="  ")
        return xml_str
