from django.db import migrations
from decimal import Decimal

def create_currencies(apps, schema_editor):
    Currency = apps.get_model('company', 'Currency')
    currencies = [
        {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'exchange_rate_to_base': Decimal('1.0000')},
        {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'exchange_rate_to_base': Decimal('1.0800')},
        {'code': 'GBP', 'name': 'British Pound', 'symbol': '£', 'exchange_rate_to_base': Decimal('0.8500')},
        {'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹', 'exchange_rate_to_base': Decimal('89.5000')},
        {'code': 'AED', 'name': 'UAE Dirham', 'symbol': 'د.إ', 'exchange_rate_to_base': Decimal('3.9600')},
    ]
    for curr in currencies:
        Currency.objects.get_or_create(code=curr['code'], defaults=curr)

def reverse_currencies(apps, schema_editor):
    Currency = apps.get_model('company', 'Currency')
    Currency.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [('company', '0004_companyprofile_financial_year_end')]
    operations = [migrations.RunPython(create_currencies, reverse_currencies)]
