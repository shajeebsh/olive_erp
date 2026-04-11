from django.contrib import admin
from .models import CompanyProfile, Currency

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol', 'is_active')
    search_fields = ('code', 'name')

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'country_code', 'email', 'vat_registered')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'address', 'phone', 'email', 'website', 'logo')
        }),
        ('Financial Configuration', {
            'fields': ('default_currency', 'fiscal_year_start_date', 'financial_year_end')
        }),
        ('Tax & Compliance', {
            'fields': ('country_code', 'state_code', 'tax_id', 'vat_registered', 'vat_registration_number')
        }),
        ('Module Configuration', {
            'description': 'Select which modules are enabled for this company.',
            'fields': ('enabled_modules',)
        }),
        ('Banking', {
            'fields': ('bank_name', 'iban')
        }),
    )
