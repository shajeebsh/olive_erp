from django.core.management.base import BaseCommand
from company.models import CompanyProfile
from finance.models import Account, JournalEntryLine
from apps.accounting.reconciliation.models import BankReconciliation
from apps.accounting.compliance.models import ComplianceDeadline, CT1Computation
from tax_engine.countries.ie.models import Director, Secretary, Shareholder
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import calendar

class Command(BaseCommand):
    help = 'Seed accounting master data'

    def handle(self, *args, **kwargs):
        company = CompanyProfile.objects.first()
        if not company:
            self.stdout.write(self.style.ERROR('No company profile found'))
            return

        company.fiscal_year_start_date = date(2025, 12, 1)
        company.address = '123 Business Park, Dublin, Ireland'
        company.phone = '+353 1 234 5678'
        company.save()

        # Delete old reconciliations to fix the date bug
        BankReconciliation.objects.filter(company=company).delete()

        # 1. Ensure bank accounts exist
        bank_account, _ = Account.objects.get_or_create(
            code='1020',
            company=company,
            defaults={'name': 'Main Bank Account', 'account_type': 'Asset'}
        )

        # 1. Seed Bank Reconciliation Months (Rolling 12 months from Dec 2025)
        for i in range(12):
            month_date = date(2025, 12, 1) + relativedelta(months=i)
            last_day = calendar.monthrange(month_date.year, month_date.month)[1]
            period_date = date(month_date.year, month_date.month, last_day)
            
            BankReconciliation.objects.get_or_create(
                company=company,
                account=bank_account,
                period_date=period_date,
                defaults={
                    'status': 'NS' if i > 0 else 'RC',
                    'opening_balance': 5000 if i == 0 else 0,
                }
            )

        # 3. Populate ComplianceDeadline
        deadlines = [
            ('VAT3 - Jan/Feb', date(date.today().year, 3, 19)),
            ('VAT3 - Mar/Apr', date(date.today().year, 5, 19)),
            ('CT1 Annual Return', date(date.today().year, 9, 23)),
            ('CRO B1 Annual Return', date(date.today().year, 11, 25)),
        ]
        for title, deadline_date in deadlines:
            ComplianceDeadline.objects.get_or_create(
                company=company,
                title=title,
                deadline_date=deadline_date,
                defaults={'status': 'PE'}
            )

        # 4. Seed statutory registers (Sample)
        Director.objects.update_or_create(
            company=company,
            first_name='John',
            last_name='Doe',
            defaults={
                'date_of_birth': date(1980, 1, 1),
                'nationality': 'Irish',
                'address_line1': '123 Main St',
                'city': 'Dublin',
                'county': 'Dublin',
                'appointment_date': date(2020, 1, 1),
                'country_code': 'IE'
            }
        )
        
        Secretary.objects.update_or_create(
            company=company,
            first_name='Jane',
            last_name='Smith',
            defaults={
                'address_line1': '456 West St',
                'city': 'Cork',
                'county': 'Cork',
                'appointment_date': date(2021, 6, 1),
                'country_code': 'IE'
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded accounting data'))
