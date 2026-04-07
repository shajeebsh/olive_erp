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
