from django.contrib import admin
from compliance.base.models import TaxPeriod, TaxFiling

@admin.register(TaxPeriod)
class TaxPeriodAdmin(admin.ModelAdmin):
    list_display = ('company', 'country', 'period_type', 'start_date', 'end_date', 'status')
    list_filter = ('country', 'period_type', 'status')

@admin.register(TaxFiling)
class TaxFilingAdmin(admin.ModelAdmin):
    list_display = ('tax_period', 'filing_type', 'filing_status', 'submitted_at')
    list_filter = ('filing_status', 'filing_type')

# Import UK-specific admins
try:
    from .countries.uk import admin as uk_admin
except ImportError:
    pass
