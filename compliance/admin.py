from django.contrib import admin
from .base.models import TaxPeriod, TaxFiling
import importlib

@admin.register(TaxPeriod)
class TaxPeriodAdmin(admin.ModelAdmin):
    list_display = ('company', 'country', 'period_type', 'start_date', 'end_date', 'status')
    list_filter = ('country', 'period_type', 'status')

@admin.register(TaxFiling)
class TaxFilingAdmin(admin.ModelAdmin):
    list_display = ('tax_period', 'filing_type', 'filing_status', 'submitted_at')
    list_filter = ('filing_status', 'filing_type')

# Import country-specific admins
try:
    from .countries.ie import admin as ie_admin
except ImportError:
    pass

try:
    from .countries.uk import admin as uk_admin
except ImportError:
    pass

try:
    importlib.import_module('compliance.countries.in.admin')
except ImportError:
    pass
