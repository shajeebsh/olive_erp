from django.core.management.base import BaseCommand
from company.models import Currency
from finance.models import Account, CompanyProfile
import datetime

class Command(BaseCommand):
    help = 'Populates initial data for Olive_ERP'

    def handle(self, *args, **options):
        # Create Default Currency
        usd, _ = Currency.objects.get_or_create(
            code='USD', 
            defaults={'name': 'US Dollar', 'symbol': '$'}
        )

        # Create Default Company
        company, _ = CompanyProfile.objects.get_or_create(
            name='Olive_ERP Demo',
            defaults={
                'address': '123 ERP St, Tech City',
                'phone': '555-0100',
                'email': 'admin@wagtailerp.com',
                'fiscal_year_start_date': datetime.date(2026, 1, 1),
                'default_currency': usd
            }
        )

        # Create Basic Chart of Accounts
        accounts = [
            ('1000', 'Cash', 'ASSET'),
            ('1100', 'Accounts Receivable', 'ASSET'),
            ('2000', 'Accounts Payable', 'LIABILITY'),
            ('3000', 'Owner Equity', 'EQUITY'),
            ('4000', 'Sales Income', 'INCOME'),
            ('5000', 'Cost of Goods Sold', 'EXPENSE'),
        ]

        for code, name, acct_type in accounts:
            Account.objects.get_or_create(
                code=code,
                defaults={'name': name, 'type': acct_type, 'company': company}
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated initial data'))
