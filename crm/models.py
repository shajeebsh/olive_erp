from django.db import models
from django.conf import settings
from inventory.models import Product

class CustomerGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


class LeadStatus(models.Model):
    name = models.CharField(max_length=50)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.name


class Lead(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('CONTACTED', 'Contacted'),
        ('QUALIFIED', 'Qualified'),
        ('PROPOSAL', 'Proposal Sent'),
        ('WON', 'Won'),
        ('LOST', 'Lost'),
    ]
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='leads', null=True, blank=True)
    lead_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    source = models.CharField(max_length=100, blank=True, help_text="e.g. Website, Referral, Trade Show")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    estimated_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.lead_name or self.company_name or f"Lead {self.pk}"


class Customer(models.Model):
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='customers', null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(CustomerGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='customers')
    company_name = models.CharField(max_length=255, blank=True)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    tax_number = models.CharField(max_length=50, blank=True)
    payment_terms = models.CharField(max_length=100, help_text="e.g. Net 30")
    state_code = models.CharField(max_length=5, blank=True, help_text="State/Province code for tax purposes")

    def __str__(self):
        return self.company_name or self.contact_person

class SalesOrder(models.Model):
    STATUS_CHOICES = (
        ('QUOTE', 'Quote'),
        ('DRAFT', 'Draft'),
        ('CONFIRMED', 'Confirmed'),
        ('SHIPPED', 'Shipped'),
        ('INVOICED', 'Invoiced'),
    )
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='sales_orders', null=True, blank=True)
    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    order_date = models.DateField()
    expected_delivery_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.order_number

class SalesOrderLine(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=18, decimal_places=3)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)
    total_price = models.DecimalField(max_digits=18, decimal_places=2)

    def __str__(self):
        return f"{self.sales_order.order_number} - {self.product.name}"


# ============================================
# Activity Model for CRM
# ============================================

class Activity(models.Model):
    """Activity model for tracking lead/customer interactions."""
    TYPE_CHOICES = [
        ('CALL', 'Call'),
        ('EMAIL', 'Email'),
        ('MEETING', 'Meeting'),
        ('NOTE', 'Note'),
        ('TASK', 'Task'),
        ('DEMO', 'Demo'),
    ]
    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='crm_activities', null=True, blank=True)
    activity_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED')
    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Relationships
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    
    # Timing
    scheduled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_at', '-created_at']
    
    def __str__(self):
        return f"{self.get_activity_type_display()}: {self.subject}"


# ============================================
# Quote Models for CRM
# ============================================

class Quote(models.Model):
    """Quote/Proposal model."""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('VIEWED', 'Viewed'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
        ('EXPIRED', 'Expired'),
    ]
    
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='quotes', null=True, blank=True)
    quote_number = models.CharField(max_length=50, unique=True)
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Relationships
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='quotes')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='quotes')
    
    # Financials
    subtotal = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    # Validity
    valid_until = models.DateField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Quote {self.quote_number} ({self.get_status_display()})"
    
    def calculate_totals(self):
        """Calculate quote totals."""
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        self.total = self.subtotal + self.tax_amount
        return self.total
    
    def convert_to_invoice(self):
        """Convert accepted quote to finance Invoice."""
        if self.status != 'ACCEPTED':
            return None
        from finance.models import Invoice
        invoice = Invoice.objects.create(
            company=self.company,
            number=self.quote_number,
            customer=self.customer,
            invoice_date=self.accepted_at,
            total_amount=self.total,
            status='UNPAID',
        )
        return invoice


class QuoteLine(models.Model):
    """Line item for Quote."""
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=18, decimal_places=3, default=1)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=18, decimal_places=2)
    
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.description[:50]
    
    def save(self, *args, **kwargs):
        discounted = self.unit_price * (1 - self.discount_percent / 100)
        self.total = self.quantity * discounted
        super().save(*args, **kwargs)


# ============================================
# Lead Scoring
# ============================================

class LeadScoring:
    """Mixing for calculating lead scores."""
    
    @staticmethod
    def calculate_score(lead):
        """Calculate 0-100 lead score based on activity and profile."""
        score = 0
        
        # Profile completeness (up to 50 points)
        if lead.email:
            score += 10
        if lead.phone:
            score += 10
        if lead.company_name:
            score += 10
        if lead.estimated_value:
            score += 10
        if lead.source:
            score += 10
        
        # Activity frequency (up to 50 points)
        activity_count = lead.activities.count()
        score += min(activity_count * 10, 50)
        
        # Age bonus (recent leads score higher)
        if lead.created_at:
            days_old = (timezone.now() - lead.created_at).days
            if days_old < 7:
                score += 10
            elif days_old < 30:
                score += 5
        
        return min(score, 100)


# Import timezone for scoring
from django.utils import timezone
