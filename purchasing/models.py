from django.db import models
from django.conf import settings
from inventory.models import Product, Warehouse

class Supplier(models.Model):
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    tax_number = models.CharField(max_length=50, blank=True)
    payment_terms = models.CharField(max_length=100)
    state_code = models.CharField(max_length=5, blank=True, help_text="State/Province code for tax purposes")

    def __str__(self):
        return self.company_name

class PurchaseOrder(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('PARTIALLY_RECEIVED', 'Partially Received'),
        ('RECEIVED', 'Received'),
        ('CANCELLED', 'Cancelled'),
    )
    po_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    order_date = models.DateField()
    expected_delivery_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    def __str__(self):
        return self.po_number

class PurchaseOrderLine(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=18, decimal_places=3)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)
    total_price = models.DecimalField(max_digits=18, decimal_places=2)
    quantity_received = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    def __str__(self):
        return f"{self.purchase_order.po_number} - {self.product.name}"

class GoodsReceivedNote(models.Model):
    grn_number = models.CharField(max_length=50, unique=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    date_received = models.DateTimeField(auto_now_add=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.grn_number
