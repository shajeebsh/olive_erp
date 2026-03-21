from django.contrib import admin
from .base.models import TaxPeriod, TaxFiling
import importlib

@admin.register(TaxPeriod)
class TaxPeriodAdmin(admin.ModelAdmin):
    list_display = ('company', 'country', 'period_type', 'start_date', 'end_date', 'status')
    list_filter = ('country', 'period_type', 'status')

@admin.register(TaxFiling)
class TaxFilingAdmin(admin.ModelAdmin):
    list_display = ('company', 'filing_type', 'period', 'status', 'due_date')
    list_filter = ('status', 'filing_type', 'company')

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
