from django.contrib import admin
from .base.models import TaxPeriod, TaxFiling

@admin.register(TaxPeriod)
class TaxPeriodAdmin(admin.ModelAdmin):
    list_display = ('company', 'country', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'country')

@admin.register(TaxFiling)
class TaxFilingAdmin(admin.ModelAdmin):
    list_display = ('tax_period', 'filing_type', 'filing_status', 'submitted_at')
    list_filter = ('filing_status', 'filing_type')

# Import country-specific admins
try:
    from .countries.ie import admin as ie_admin
except ImportError as e:
    pass
