from django.test import TestCase
from company.models import CompanyProfile
from finance.models import Account
from apps.accounting.assets.models import FixedAsset
from apps.accounting.reconciliation.models import BankReconciliation
from apps.accounting.compliance.models import ComplianceDeadline
from datetime import date

class AccountingModelTest(TestCase):
    def setUp(self):
        self.company = CompanyProfile.objects.create(
            name="Test Company",
            country_code="IE",
            email="test@example.com",
            address="123 Test St",
            phone="1234567890",
            fiscal_year_start_date=date(2026, 1, 1)
        )
        self.account = Account.objects.create(
            code="1020",
            name="Bank",
            account_type="Asset",
            company=self.company
        )
        self.deprec_account = Account.objects.create(
            code="1030",
            name="Acc Dep",
            account_type="Asset",
            company=self.company
        )
        self.exp_account = Account.objects.create(
            code="5010",
            name="Dep Exp",
            account_type="Expense",
            company=self.company
        )

    def test_fixed_asset_creation(self):
        asset = FixedAsset.objects.create(
            name="Laptop",
            asset_code="AST001",
            company=self.company,
            asset_account=self.account,
            accumulated_depreciation_account=self.deprec_account,
            depreciation_expense_account=self.exp_account,
            purchase_date=date.today(),
            purchase_value=1000,
            depreciation_rate=20
        )
        self.assertEqual(asset.name, "Laptop")
        self.assertEqual(asset.net_book_value, 1000)

    def test_bank_reconciliation_creation(self):
        recon = BankReconciliation.objects.create(
            company=self.company,
            account=self.account,
            period_date=date.today(),
            statement_balance=500,
            book_balance=500,
            actual_closing_balance=0
        )
        self.assertEqual(recon.difference, 0)

    def test_compliance_deadline_creation(self):
        deadline = ComplianceDeadline.objects.create(
            company=self.company,
            title="VAT3 Return",
            deadline_date=date.today()
        )
        self.assertEqual(deadline.status, 'PE')
