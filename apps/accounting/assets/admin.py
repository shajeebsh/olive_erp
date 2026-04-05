from django.contrib import admin
from apps.accounting.assets.models import FixedAsset


@admin.register(FixedAsset)
class FixedAssetAdmin(admin.ModelAdmin):
    list_display = ['asset_code', 'name', 'company', 'purchase_value', 'net_book_value', 'depreciation_method', 'is_disposed']
    list_filter = ['company', 'depreciation_method', 'is_disposed']
    search_fields = ['asset_code', 'name']
    readonly_fields = ['created_at', 'updated_at', 'net_book_value', 'accumulated_depreciation']
