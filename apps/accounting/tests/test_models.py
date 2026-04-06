from django.test import TestCase
from django.core.exceptions import ValidationError
from company.models import CompanyProfile
from finance.models import Account, CostCentre
from apps.accounting.assets.models import FixedAsset
from apps.accounting.reconciliation.models import BankReconciliation
from apps.accounting.compliance.models import ComplianceDeadline
from tax_engine.countries.ie.models import Director, Secretary, Shareholder
from tax_engine.countries.ie.rbo import BeneficialOwner
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


class CostCentreModelTest(TestCase):
    def setUp(self):
        self.company = CompanyProfile.objects.create(
            name="Test Company",
            country_code="IE",
            email="test@example.com",
            address="123 Test St",
            phone="1234567890",
            fiscal_year_start_date=date(2026, 1, 1)
        )
        self.cc1 = CostCentre.objects.create(
            code="CC001",
            name="IT Department",
            company=self.company
        )

    def test_cost_centre_creation(self):
        self.assertEqual(self.cc1.code, "CC001")
        self.assertEqual(self.cc1.name, "IT Department")
        self.assertTrue(self.cc1.is_active)

    def test_cost_centre_unique_code_per_company(self):
        with self.assertRaises(Exception):
            CostCentre.objects.create(
                code="CC001",
                name="Marketing",
                company=self.company
            )

    def test_cost_centre_validation_unique_together(self):
        with self.assertRaises(Exception):
            CostCentre.objects.create(
                code="CC001",
                name="IT Dept 2",
                company=self.company
            )


class DirectorModelTest(TestCase):
    def setUp(self):
        self.company = CompanyProfile.objects.create(
            name="Test Company",
            country_code="IE",
            email="test@example.com",
            address="123 Test St",
            phone="1234567890",
            fiscal_year_start_date=date(2026, 1, 1)
        )
        self.director = Director.objects.create(
            company=self.company,
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1980, 1, 1),
            nationality="Irish",
            address_line1="123 Main St",
            city="Dublin",
            county="Dublin",
            country="Ireland",
            country_code="IE",
            appointment_date=date(2020, 1, 1)
        )

    def test_director_is_active_by_default(self):
        self.assertTrue(self.director.is_active)

    def test_director_becomes_inactive_on_resignation(self):
        self.director.resignation_date = date(2025, 1, 1)
        self.assertFalse(self.director.is_active)


class SecretaryModelTest(TestCase):
    def setUp(self):
        self.company = CompanyProfile.objects.create(
            name="Test Company",
            country_code="IE",
            email="test@example.com",
            address="123 Test St",
            phone="1234567890",
            fiscal_year_start_date=date(2026, 1, 1)
        )
        self.secretary = Secretary.objects.create(
            company=self.company,
            first_name="Jane",
            last_name="Smith",
            address_line1="456 High St",
            city="Dublin",
            county="Dublin",
            country="Ireland",
            country_code="IE",
            appointment_date=date(2021, 1, 1)
        )

    def test_secretary_is_active_by_default(self):
        self.assertTrue(self.secretary.is_active)

    def test_secretary_name_property(self):
        self.assertEqual(self.secretary.name, "Jane Smith")


class ShareholderModelTest(TestCase):
    def setUp(self):
        self.company = CompanyProfile.objects.create(
            name="Test Company",
            country_code="IE",
            email="test@example.com",
            address="123 Test St",
            phone="1234567890",
            fiscal_year_start_date=date(2026, 1, 1)
        )
        self.shareholder = Shareholder.objects.create(
            company=self.company,
            first_name="Bob",
            last_name="Wilson",
            address_line1="789 New St",
            city="Cork",
            county="Cork",
            country="Ireland",
            country_code="IE",
            ordinary_shares_held=100,
            percentage_held=10.5,
            date_joined=date(2022, 1, 1)
        )

    def test_shareholder_name_property(self):
        self.assertEqual(self.shareholder.name, "Bob Wilson")

    def test_shareholder_default_share_class(self):
        self.assertEqual(self.shareholder.share_class, "Ordinary")
