from django.core.management.base import BaseCommand
from company.models import CompanyProfile
from compliance.models import TaxFiling
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Seeds initial Ireland compliance deadlines for testing'

    def handle(self, *args, **options):
        ie_companies = CompanyProfile.objects.filter(country_code="IE")
        if not ie_companies.exists():
            self.stdout.write(self.style.WARNING('No Ireland (IE) companies found. Skipped seeding.'))
            return
            
        for company in ie_companies:
            TaxFiling.objects.get_or_create(
                company=company, filing_type='vat_return', period='2024-Q1',
                defaults={'due_date': datetime.date(2024, 7, 23), 'status': 'overdue'}
            )
            TaxFiling.objects.get_or_create(
                company=company, filing_type='paye_prsi', period='July 2024',
                defaults={'due_date': datetime.date(2024, 8, 23), 'status': 'overdue'}
            )
            TaxFiling.objects.get_or_create(
                company=company, filing_type='cro_b1', period='2024',
                defaults={'due_date': timezone.now().date() + datetime.timedelta(days=15), 'status': 'pending'}
            )
            TaxFiling.objects.get_or_create(
                company=company, filing_type='corp_tax', period='2023',
                defaults={'due_date': timezone.now().date() + datetime.timedelta(days=45), 'status': 'draft'}
            )
            TaxFiling.objects.get_or_create(
                company=company, filing_type='rbo', period='2024',
                defaults={'due_date': timezone.now().date() + datetime.timedelta(days=100), 'status': 'draft'}
            )
            
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded deadlines for {ie_companies.count()} IE company(ies).'))
