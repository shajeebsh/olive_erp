from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_lazy as _

class HSNCode(models.Model):
    """
    Harmonized System of Nomenclature (HSN) for goods.
    Used for classification of goods under GST.
    """
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='hsn_codes')
    code = models.CharField(max_length=8, help_text="4, 6 or 8 digit HSN Code")
    description = models.CharField(max_length=255)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Default GST Rate (%)")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("HSN Code")
        verbose_name_plural = _("HSN Codes")
        unique_together = ['company', 'code']
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.description[:30]}"


class SACCode(models.Model):
    """
    Service Accounting Code (SAC) for services.
    Used for classification of services under GST.
    """
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='sac_codes')
    code = models.CharField(max_length=6, help_text="6 digit SAC Code")
    description = models.CharField(max_length=255)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Default GST Rate (%)")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("SAC Code")
        verbose_name_plural = _("SAC Codes")
        unique_together = ['company', 'code']
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.description[:30]}"


class ProductTaxClassification(models.Model):
    """
    Mapping of internal products/services to HSN/SAC codes.
    """
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='product_tax_classifications')
    PRODUCT_TYPES = (
        ('goods', _('Goods (HSN)')),
        ('service', _('Service (SAC)')),
    )
    
    product = models.OneToOneField('inventory.Product', on_delete=models.CASCADE, related_name='india_tax_class')
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPES)
    
    hsn_code = models.ForeignKey(HSNCode, on_delete=models.SET_NULL, null=True, blank=True)
    sac_code = models.ForeignKey(SACCode, on_delete=models.SET_NULL, null=True, blank=True)
    
    exempt_from_gst = models.BooleanField(default=False)
    reverse_charge_applicable = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _("Product Tax Classification")
        verbose_name_plural = _("Product Tax Classifications")

    def __str__(self):
        code = self.hsn_code if self.product_type == 'goods' else self.sac_code
        return f"{self.product.name} - {code}"

    def get_tax_rate(self):
        if self.exempt_from_gst:
            return 0
        if self.product_type == 'goods' and self.hsn_code:
            return self.hsn_code.gst_rate
        if self.product_type == 'service' and self.sac_code:
            return self.sac_code.gst_rate
        return None
