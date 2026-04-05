from django.contrib import admin
from apps.accounting.compliance.models import ComplianceDeadline, ChecklistItem, CT1Computation, Dividend, RelatedPartyTransaction


@admin.register(ComplianceDeadline)
class ComplianceDeadlineAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'deadline_date', 'status', 'responsible_party']
    list_filter = ['company', 'status']
    search_fields = ['title']


@admin.register(CT1Computation)
class CT1ComputationAdmin(admin.ModelAdmin):
    list_display = ['company', 'period_start', 'period_end', 'taxable_profit', 'tax_payable', 'is_finalized']
    list_filter = ['company', 'is_finalized']


@admin.register(Dividend)
class DividendAdmin(admin.ModelAdmin):
    list_display = ['voucher_number', 'company', 'shareholder_name', 'declaration_date', 'net_amount', 'is_paid']
    list_filter = ['company', 'is_paid']


@admin.register(RelatedPartyTransaction)
class RelatedPartyTransactionAdmin(admin.ModelAdmin):
    list_display = ['company', 'party_name', 'relationship', 'transaction_date', 'amount', 'is_arm_length']
    list_filter = ['company', 'relationship', 'is_arm_length']
