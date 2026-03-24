from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from company.models import Currency
from finance.models import Account
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populates initial master data for Olive ERP'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting initial data creation...'))
        self.create_currencies()
        self.create_chart_of_accounts()
        self.create_tax_rates()
        self.stdout.write(self.style.SUCCESS('Initial data creation completed!'))
    
    def create_currencies(self):
        currencies = [
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'exchange_rate_to_base': Decimal('1.0000')},
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'exchange_rate_to_base': Decimal('1.0800')},
            {'code': 'GBP', 'name': 'British Pound', 'symbol': '£', 'exchange_rate_to_base': Decimal('0.8500')},
            {'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹', 'exchange_rate_to_base': Decimal('89.5000')},
            {'code': 'AED', 'name': 'UAE Dirham', 'symbol': 'د.إ', 'exchange_rate_to_base': Decimal('3.9600')},
        ]
        created_count = 0
        for curr_data in currencies:
            currency, created = Currency.objects.get_or_create(
                code=curr_data['code'],
                defaults={
                    'name': curr_data['name'],
                    'symbol': curr_data['symbol'],
                    'exchange_rate_to_base': curr_data['exchange_rate_to_base']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Created currency: {curr_data["code"]} - {curr_data["name"]}')
        self.stdout.write(self.style.SUCCESS(f'  Currencies: {created_count} created'))
    
    def create_chart_of_accounts(self):
        accounts = [
            {'code': '1000', 'name': 'Cash', 'account_type': 'Asset', 'group_type': 'Ledger'},
            {'code': '1010', 'name': 'Bank Account', 'account_type': 'Asset', 'group_type': 'Ledger'},
            {'code': '1100', 'name': 'Accounts Receivable', 'account_type': 'Asset', 'group_type': 'Ledger'},
            {'code': '1200', 'name': 'Inventory', 'account_type': 'Asset', 'group_type': 'Ledger'},
            {'code': '2000', 'name': 'Accounts Payable', 'account_type': 'Liability', 'group_type': 'Ledger'},
            {'code': '2100', 'name': 'Tax Payable', 'account_type': 'Liability', 'group_type': 'Ledger'},
            {'code': '3000', 'name': 'Capital', 'account_type': 'Equity', 'group_type': 'Ledger'},
            {'code': '3100', 'name': 'Retained Earnings', 'account_type': 'Equity', 'group_type': 'Ledger'},
            {'code': '4000', 'name': 'Sales Revenue', 'account_type': 'Income', 'group_type': 'Ledger'},
            {'code': '5000', 'name': 'Cost of Goods Sold', 'account_type': 'Expense', 'group_type': 'Ledger'},
            {'code': '5100', 'name': 'Salaries & Wages', 'account_type': 'Expense', 'group_type': 'Ledger'},
            {'code': '5200', 'name': 'Rent', 'account_type': 'Expense', 'group_type': 'Ledger'},
        ]
        created_count = 0
        for acc_data in accounts:
            account, created = Account.objects.get_or_create(
                code=acc_data['code'],
                defaults={
                    'name': acc_data['name'],
                    'account_type': acc_data['account_type'],
                    'group_type': acc_data['group_type'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f'  Chart of Accounts: {created_count} accounts created'))
    
    def create_tax_rates(self):
        try:
            from compliance.models import TaxRate
            tax_rates = [
                {'rate': 23.0, 'name': 'VAT Standard (23%)', 'country': 'IE'},
                {'rate': 13.5, 'name': 'VAT Reduced (13.5%)', 'country': 'IE'},
                {'rate': 20.0, 'name': 'VAT Standard (20%)', 'country': 'GB'},
                {'rate': 5.0, 'name': 'GST (5%)', 'country': 'IN'},
                {'rate': 18.0, 'name': 'GST (18%)', 'country': 'IN'},
                {'rate': 5.0, 'name': 'VAT Standard (5%)', 'country': 'AE'},
            ]
            created_count = 0
            for rate_data in tax_rates:
                rate, created = TaxRate.objects.get_or_create(
                    rate=rate_data['rate'],
                    country=rate_data['country'],
                    defaults={'name': rate_data['name']}
                )
                if created:
                    created_count += 1
            self.stdout.write(self.style.SUCCESS(f'  Tax Rates: {created_count} created'))
        except ImportError:
            self.stdout.write(self.style.WARNING('  TaxRate model not found - skipping'))
