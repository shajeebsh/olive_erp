import importlib
from django.contrib import admin

in_models = importlib.import_module('tax_engine.countries.in.models')
in_tds = importlib.import_module('tax_engine.countries.in.tds')
in_ewaybill = importlib.import_module('tax_engine.countries.in.ewaybill')
in_einvoice = importlib.import_module('tax_engine.countries.in.einvoice')

HSNCode = in_models.HSNCode
SACCode = in_models.SACCode
ProductTaxClassification = in_models.ProductTaxClassification

TDSSection = in_tds.TDSSection
TDSDeduction = in_tds.TDSDeduction
TDSChallan = in_tds.TDSChallan
TDSReturnQuarterly = in_tds.TDSReturnQuarterly

EWayBill = in_ewaybill.EWayBill
EWayBillItem = in_ewaybill.EWayBillItem

EInvoiceIRN = in_einvoice.EInvoiceIRN


@admin.register(HSNCode)
class HSNCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'gst_rate', 'is_active', 'company')
    list_filter = ('is_active', 'gst_rate', 'company')
    search_fields = ('code', 'description')

@admin.register(SACCode)
class SACCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'gst_rate', 'is_active', 'company')
    list_filter = ('is_active', 'gst_rate', 'company')
    search_fields = ('code', 'description')

@admin.register(ProductTaxClassification)
class ProductTaxClassificationAdmin(admin.ModelAdmin):
    list_display = ('product', 'product_type', 'hsn_code', 'sac_code', 'exempt_from_gst', 'company')
    list_filter = ('product_type', 'exempt_from_gst', 'company')
    search_fields = ('product__name', 'hsn_code__code', 'sac_code__code')

@admin.register(TDSSection)
class TDSSectionAdmin(admin.ModelAdmin):
    list_display = ('section_code', 'party_type', 'rate_percent', 'threshold_limit_single', 'threshold_limit_aggregate', 'company')
    list_filter = ('party_type', 'company')
    search_fields = ('section_code', 'description')

@admin.register(TDSDeduction)
class TDSDeductionAdmin(admin.ModelAdmin):
    list_display = ('bill', 'vendor', 'section', 'date_of_deduction', 'base_amount', 'tds_amount', 'company')
    list_filter = ('section', 'date_of_deduction', 'company')
    search_fields = ('bill__invoice_number', 'vendor__name')
    date_hierarchy = 'date_of_deduction'

@admin.register(TDSChallan)
class TDSChallanAdmin(admin.ModelAdmin):
    list_display = ('challan_number', 'bsr_code', 'date_of_deposit', 'amount', 'company')
    list_filter = ('date_of_deposit', 'company')
    search_fields = ('challan_number', 'bsr_code')
    date_hierarchy = 'date_of_deposit'

@admin.register(TDSReturnQuarterly)
class TDSReturnQuarterlyAdmin(admin.ModelAdmin):
    list_display = ('financial_year', 'quarter', 'form_type', 'status', 'date_filed', 'company')
    list_filter = ('financial_year', 'quarter', 'form_type', 'status', 'company')
    search_fields = ('prn_number',)

class EWayBillItemInline(admin.TabularInline):
    model = EWayBillItem
    extra = 1

@admin.register(EWayBill)
class EWayBillAdmin(admin.ModelAdmin):
    list_display = ('ewaybill_no', 'doc_no', 'doc_date', 'status', 'total_value', 'company')
    list_filter = ('status', 'doc_date', 'trans_mode', 'company')
    search_fields = ('ewaybill_no', 'doc_no', 'from_trd_name', 'to_trd_name')
    date_hierarchy = 'doc_date'
    inlines = [EWayBillItemInline]

@admin.register(EInvoiceIRN)
class EInvoiceIRNAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'irn', 'status', 'ack_no', 'ack_date', 'company')
    list_filter = ('status', 'ack_date', 'company')
    search_fields = ('irn', 'ack_no', 'invoice__invoice_number')
    date_hierarchy = 'ack_date'
