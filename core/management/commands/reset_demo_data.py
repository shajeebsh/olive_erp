from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection
from company.models import CompanyProfile, Currency

User = get_user_model()

class Command(BaseCommand):
    help = 'Reset and reseed development data for accounting testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep-company',
            action='store_true',
            help='Keep existing company and just reset accounting data',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Resetting development data..."))
        
        if options['keep_company']:
            self.reset_accounting_data()
        else:
            self.full_reset()
        
        self.stdout.write(self.style.SUCCESS("Running sample data generation..."))
        from core.management.commands.generate_sample_data import Command as GenerateCommand
        gen_cmd = GenerateCommand(stdout=self.stdout)
        # Skip clear_existing since we just cleared the data
        gen_cmd.handle(clear_existing=False, num_months=12)
        
        self.stdout.write(self.style.SUCCESS("Reset complete!"))

    def full_reset(self):
        self.stdout.write("Clearing all data using SQL...")
        
        # Use raw SQL to clear tables to avoid FK issues
        tables_to_clear = [
            'finance_journalentryline',
            'finance_journalentry',
            'finance_invoiceitem',
            'finance_invoice',
            'inventory_stockmovement',
            'inventory_stocklevel',
            'inventory_product',
            'inventory_category',
            'inventory_warehouse',
            'crm_salesorderline',
            'crm_salesorder',
            'crm_customer',
            'hr_attendance',
            'hr_leaverequest',
            'hr_employee',
            'hr_department',
            'projects_task',
            'projects_project',
            'purchasing_goodsreceivednote',
            'purchasing_purchaseorderline',
            'purchasing_purchaseorder',
            'purchasing_supplier',
            'tax_engine_beneficialowner',
            'tax_engine_taxfiling',
            'tax_engine_taxperiod',
            'apps_accounting_fixedasset',
            'apps_accounting_bankreconciliation',
            'apps_accounting_compliancedeadline',
            'apps_accounting_ct1computation',
            'apps_accounting_dividend',
            'apps_accounting_relatedpartytransaction',
            'finance_account',
            'company_companyprofile',
            'company_currency',
        ]
        
        from django.db import connection
        with connection.cursor() as cursor:
            for table in tables_to_clear:
                try:
                    # Check if table exists
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    if cursor.fetchone():
                        cursor.execute(f"DELETE FROM {table}")
                        self.stdout.write(f"  Cleared {table}")
                    else:
                        self.stdout.write(f"  Table {table} does not exist, skipping")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  Could not clear {table}: {e}"))
        
        # Clear users
        try:
            User.objects.filter(username='admin').delete()
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error clearing users: {e}"))
        
        self.stdout.write(self.style.SUCCESS("All data cleared"))

    def reset_accounting_data(self):
        self.stdout.write("Clearing accounting data only...")
        
        # Clear in order of dependencies - use delete() with ignore_params for protected
        try:
            from finance.models import JournalEntryLine, JournalEntry
            JournalEntryLine.objects.all().delete()
            JournalEntry.objects.all().delete()
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error clearing journal: {e}"))
        
        try:
            from apps.accounting.assets.models import FixedAsset
            from apps.accounting.reconciliation.models import BankReconciliation
            from apps.accounting.compliance.models import (
                ComplianceDeadline, CT1Computation, Dividend, RelatedPartyTransaction
            )
            FixedAsset.objects.all().delete()
            BankReconciliation.objects.all().delete()
            ComplianceDeadline.objects.all().delete()
            CT1Computation.objects.all().delete()
            Dividend.objects.all().delete()
            RelatedPartyTransaction.objects.all().delete()
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error clearing accounting: {e}"))
        
        self.stdout.write(self.style.SUCCESS("Accounting data cleared"))
