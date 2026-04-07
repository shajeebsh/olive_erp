from django.db import models
from django.conf import settings
from company.models import CompanyProfile

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name

class Product(models.Model):
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    unit_of_measure = models.CharField(max_length=20) # pcs, kg
    selling_price = models.DecimalField(max_digits=18, decimal_places=2)
    cost_price = models.DecimalField(max_digits=18, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.sku} - {self.name}"

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class StockLevel(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity_on_hand = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_reserved = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    reorder_level = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    class Meta:
        unique_together = ('product', 'warehouse')

    def __str__(self):
        return f"{self.product.name} @ {self.warehouse.name}"

class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ('PURCHASE', 'Purchase'),
        ('SALE', 'Sale'),
        ('ADJUSTMENT', 'Adjustment'),
        ('TRANSFER', 'Transfer'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=18, decimal_places=3)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    reference = models.CharField(max_length=100) # e.g. PO#123
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.movement_type} - {self.product.sku}"
