from django.contrib import admin
from .models import CompanyOfficer, ConfirmationStatement, PersonWithSignificantControl

@admin.register(CompanyOfficer)
class CompanyOfficerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'company', 'role', 'appointment_date', 'is_psc']
    list_filter = ['company', 'role', 'is_psc', 'nationality']
    search_fields = ['first_name', 'last_name', 'company__name']
    date_hierarchy = 'appointment_date'
    
    fieldsets = (
        ('Personal Details', {
            'fields': ('title', 'first_name', 'last_name', 'former_names', 'date_of_birth', 'nationality', 'country_of_residence')
        }),
        ('Service Address (Public)', {
            'fields': ('service_address_line1', 'service_address_line2', 'service_address_city', 
                      'service_address_county', 'service_address_postcode', 'service_address_country')
        }),
        ('Residential Address (Private)', {
            'fields': ('residential_address_line1', 'residential_address_line2', 'residential_address_city',
                      'residential_address_county', 'residential_address_postcode', 'residential_address_country')
        }),
        ('Appointment', {
            'fields': ('role', 'appointment_date', 'resignation_date', 'occupation')
        }),
        ('PSC', {
            'fields': ('is_psc',)
        }),
    )

@admin.register(ConfirmationStatement)
class ConfirmationStatementAdmin(admin.ModelAdmin):
    list_display = ['company', 'period_end', 'statement_date', 'filing_number', 'filed_at']
    list_filter = ['company', 'is_trading']
    date_hierarchy = 'period_end'
    
    filter_horizontal = ['current_officers']

@admin.register(PersonWithSignificantControl)
class PSCAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'company', 'nature_of_control', 'percentage_held', 'notified_date']
    list_filter = ['company', 'nature_of_control', 'is_corporate']
    search_fields = ['first_name', 'last_name', 'corporate_name']
