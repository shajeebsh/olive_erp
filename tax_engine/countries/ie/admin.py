from django.contrib import admin
from .models import Director, Secretary, Shareholder, OrdinaryShare, PreferenceShare
from .rbo import BeneficialOwner, RBORegistration

@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'company', 'appointment_date', 'is_chairperson']
    list_filter = ['company', 'is_chairperson', 'nationality']
    search_fields = ['first_name', 'last_name']

@admin.register(Secretary)
class SecretaryAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'company', 'appointment_date']
    list_filter = ['company', 'is_corporate']

@admin.register(Shareholder)
class ShareholderAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'company', 'ordinary_shares_held', 'percentage_held']
    list_filter = ['company', 'is_corporate']
    search_fields = ['first_name', 'last_name', 'corporate_name']

@admin.register(OrdinaryShare)
class OrdinaryShareAdmin(admin.ModelAdmin):
    list_display = ['company', 'total_issued', 'nominal_value', 'total_nominal_value']
    list_filter = ['company']

@admin.register(BeneficialOwner)
class BeneficialOwnerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'company', 'percentage_held', 'is_verified']
    list_filter = ['company', 'is_verified', 'nationality']
    search_fields = ['first_name', 'last_name']

@admin.register(RBORegistration)
class RBORegistrationAdmin(admin.ModelAdmin):
    list_display = ['company', 'filing_date', 'status', 'registration_number']
    list_filter = ['company', 'status']
