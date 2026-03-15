from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import User

class EWayBill(models.Model):
    """
    Electronic Way Bill required for movement of goods in India
    exceeding ₹50,000 threshold.
    """
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='eway_bills_in')
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('generated', _('Generated')),
        ('cancelled', _('Cancelled')),
        ('rejected', _('Rejected by Recipient')),
    )

    TRANS_MODE_CHOICES = (
        ('1', _('Road')),
        ('2', _('Rail')),
        ('3', _('Air')),
        ('4', _('Ship')),
    )

    doc_no = models.CharField(max_length=20, help_text="Invoice or Delivery Challan Number")
    doc_date = models.DateField()
    ewaybill_no = models.CharField(max_length=12, unique=True, null=True, blank=True)
    generated_date = models.DateTimeField(null=True, blank=True)
    valid_upto = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Supplier Details
    from_gstin = models.CharField(max_length=15)
    from_trd_name = models.CharField(max_length=100)
    from_pincode = models.CharField(max_length=6)
    from_state_code = models.CharField(max_length=2)

    # Recipient Details 
    to_gstin = models.CharField(max_length=15, null=True, blank=True) # Could be UR for B2C
    to_trd_name = models.CharField(max_length=100)
    to_pincode = models.CharField(max_length=6)
    to_state_code = models.CharField(max_length=2)

    # Item Total Details
    total_value = models.DecimalField(max_digits=12, decimal_places=2)
    cgst_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sgst_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    igst_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cess_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Transportation Details
    transer_doc_no = models.CharField(max_length=20, null=True, blank=True, help_text="LR/RR/Airway Bill/Bill of Lading")
    transer_doc_date = models.DateField(null=True, blank=True)
    trans_mode = models.CharField(max_length=1, choices=TRANS_MODE_CHOICES)
    trans_distance = models.IntegerField(help_text="Distance in KM")
    transporter_id = models.CharField(max_length=15, null=True, blank=True, help_text="GSTIN/TRANSIN of Transporter")
    transporter_name = models.CharField(max_length=100, null=True, blank=True)
    vehicle_no = models.CharField(max_length=20, null=True, blank=True)

    invoice = models.ForeignKey('finance.Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='ewaybills')
    
    class Meta:
        verbose_name = _("E-Way Bill")
        verbose_name_plural = _("E-Way Bills")
        ordering = ['-doc_date', '-id']

    def __str__(self):
        return f"EWB {self.ewaybill_no or 'Draft'} - {self.doc_no}"


class EWayBillItem(models.Model):
    ewaybill = models.ForeignKey(EWayBill, on_delete=models.CASCADE, related_name='itemList')
    product_name = models.CharField(max_length=100)
    hsn_code = models.CharField(max_length=8)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    qty_unit = models.CharField(max_length=10, default="NOS")
    taxable_amount = models.DecimalField(max_digits=12, decimal_places=2)
    cgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    igst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)


class EWayBillGenerator:
    """Helper class to generate E-Way Bills from invoices."""
    
    def __init__(self, company):
        self.company = company
        
    def check_eway_bill_required(self, invoice):
        """Check if an invoice requires an E-Way Bill."""
        # Only B2B or B2C invoices involving goods (not services only)
        # Threshold is Rs. 50,000 for inter-state (limits vary by state for intra-state)
        
        has_goods = any(item.product.type == 'product' for item in invoice.items.all())
        if not has_goods:
            return False, "Contains only services"
            
        is_inter_state = self.company.state_code != invoice.customer.state_code
        threshold = 50000 # Default threshold
        
        # In a real app, look up state-specific threshold for intra-state
        
        if invoice.total_amount > threshold:
            return True, f"Value exceeds threshold ({invoice.total_amount} > {threshold})"
            
        return False, "Value below threshold"
