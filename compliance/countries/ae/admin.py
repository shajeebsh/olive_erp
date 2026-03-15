from django.contrib import admin
from .excise import ExciseGoodsCategory, ExciseProduct, ExciseDeclaration
from .corporate_tax import CorporateTaxReturn, TaxLoss, FreeZonePerson

@admin.register(ExciseGoodsCategory)
class ExciseGoodsCategoryAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'rate', 'requires_marking', 'effective_from']
    list_filter = ['requires_marking']
    search_fields = ['display_name', 'description']

@admin.register(ExciseProduct)
class ExciseProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'category', 'effective_rate', 'has_digital_stamp']
    list_filter = ['category', 'has_digital_stamp']
    search_fields = ['product__name']

@admin.register(ExciseDeclaration)
class ExciseDeclarationAdmin(admin.ModelAdmin):
    list_display = ['company', 'declaration_period', 'total_excise_due', 'payment_made']
    list_filter = ['company', 'payment_made']
    date_hierarchy = 'declaration_period'

@admin.register(CorporateTaxReturn)
class CorporateTaxReturnAdmin(admin.ModelAdmin):
    list_display = ['company', 'tax_period_start', 'tax_period_end', 'taxable_income', 'tax_amount', 'status']
    list_filter = ['company', 'status', 'is_free_zone_person']
    date_hierarchy = 'tax_period_end'

@admin.register(TaxLoss)
class TaxLossAdmin(admin.ModelAdmin):
    list_display = ['company', 'loss_year', 'loss_amount', 'utilized_amount', 'is_active']
    list_filter = ['company', 'loss_year', 'is_active']

@admin.register(FreeZonePerson)
class FreeZonePersonAdmin(admin.ModelAdmin):
    list_display = ['company', 'free_zone_name', 'license_expiry_date']
    list_filter = ['free_zone_name']
    search_fields = ['company__name']
