from django.test import TestCase
from decimal import Decimal
from datetime import date
from django.contrib.auth import get_user_model
from company.models import CompanyProfile, Currency
from crm.models import Customer
from purchasing.models import Supplier
from finance.models import Invoice, Account
import importlib

User = get_user_model()

# Import using importlib because 'in' is a reserved keyword
in_init = importlib.import_module('compliance.countries.in')
in_tds_calc = importlib.import_module('compliance.countries.in.tds_calculator')
in_calendar = importlib.import_module('compliance.countries.in.calendar')

IndiaTaxEngine = in_init.IndiaTaxEngine
TDSCalculator = in_tds_calc.TDSCalculator
IndiaComplianceCalendar = in_calendar.IndiaComplianceCalendar


class TestIndiaTaxEngine(TestCase):
    
    def setUp(self):
        self.currency = Currency.objects.create(code='INR', name='Indian Rupee', symbol='₹')
        self.company = CompanyProfile.objects.create(
            name='Test India Pvt Ltd',
            state_code='27', # Maharashtra
            country='IN',
            fiscal_year_start_date=date(2023, 4, 1),
            default_currency=self.currency
        )
        self.engine = IndiaTaxEngine()
        self.engine.company = self.company
        
    def test_intra_state_gst_calculation(self):
        """Test calculation of CGST and SGST for same-state sale"""
        result = self.engine.calculate_tax(
            amount=Decimal('1000.00'),
            tax_type='18',
            customer_location='27', # Maharashtra
            place_of_supply='27'    # Maharashtra
        )
        
        self.assertEqual(result['type'], 'intra_state')
        self.assertEqual(result['total_gst'], Decimal('180.00'))
        self.assertEqual(result['cgst'], Decimal('90.00'))
        self.assertEqual(result['sgst'], Decimal('90.00'))
        self.assertEqual(result['igst'], Decimal('0.00'))
        
    def test_inter_state_gst_calculation(self):
        """Test calculation of IGST for cross-state sale"""
        result = self.engine.calculate_tax(
            amount=Decimal('5000.00'),
            tax_type='12',
            customer_location='29', # Karnataka
            place_of_supply='27'    # Maharashtra
        )
        
        self.assertEqual(result['type'], 'inter_state')
        self.assertEqual(result['total_gst'], Decimal('600.00'))
        self.assertEqual(result['cgst'], Decimal('0.00'))
        self.assertEqual(result['sgst'], Decimal('0.00'))
        self.assertEqual(result['igst'], Decimal('600.00'))
        
    def test_gstin_validation(self):
        """Test validation of Indian GSTIN format"""
        # Valid GSTIN
        is_valid, msg = self.engine.validate_tax_number('27AAPFU0939F1Z5')
        self.assertTrue(is_valid)
        
        # Invalid state code structure (must be numeric 01-37)
        is_valid, msg = self.engine.validate_tax_number('XXAAPFU0939F1Z5')
        self.assertFalse(is_valid)
        self.assertIn("state code", msg.lower())
        
        # Invalid PAN structure (15 chars total, but PAN part is wrong)
        is_valid, msg = self.engine.validate_tax_number('2712345678901Z5')
        self.assertFalse(is_valid)
        self.assertTrue("pan format" in msg.lower() or "pan structure" in msg.lower())
        
    def test_hsn_validation(self):
        """Test validation of HSN/SAC codes"""
        is_valid, _ = self.engine.validate_hsn_sac('1234', 'hsn')
        self.assertTrue(is_valid)
        
        is_valid, _ = self.engine.validate_hsn_sac('991234', 'sac')
        self.assertTrue(is_valid)
        
        # Invalid length
        is_valid, _ = self.engine.validate_hsn_sac('123', 'hsn')
        self.assertFalse(is_valid)


class TestTDS(TestCase):
    
    def setUp(self):
        self.currency = Currency.objects.create(code='INR', name='Indian Rupee', symbol='₹')
        self.company = CompanyProfile.objects.create(
            name='Test India Pvt Ltd',
            state_code='27',
            country='IN',
            fiscal_year_start_date=date(2023, 4, 1),
            default_currency=self.currency
        )
        # Use importlib to get the TDSSection model
        in_tds_models = importlib.import_module('compliance.countries.in.tds')
        self.TDSSection = in_tds_models.TDSSection
        
        self.calculator = TDSCalculator(company=self.company)
        
        # Create a sample account for TDS payable
        self.payable_account = Account.objects.create(
            company=self.company,
            code='200001',
            name='TDS Payable Account',
            account_type='Liability',
            group_type='Ledger'
        )
        
    def test_tds_threshold_single_bill(self):
        """Test TDS checking for a single bill threshold (like section 194C)"""
        vendor = Supplier.objects.create(
            company_name="Test Contractor",
            tax_number="PAN123456A",
            email="test@example.com",
            phone="1234567890",
            address="Test Address",
            payment_terms="Net 30"
        )
        
        section = self.TDSSection.objects.create(
            company=self.company,
            section_code='194C',
            description='Contractor Payments',
            party_type='company',
            rate_percent=Decimal('2.0'),
            threshold_limit_single=Decimal('30000.00'),
            threshold_limit_aggregate=Decimal('100000.00'),
            payable_account=self.payable_account
        )
        
        # Below threshold
        self.assertFalse(self.calculator.check_threshold(vendor, section, Decimal('25000.00'), date(2023, 5, 1)))
        
        # Above single bill threshold
        self.assertTrue(self.calculator.check_threshold(vendor, section, Decimal('35000.00'), date(2023, 5, 1)))


class TestIndiaCalendar(TestCase):
    
    def setUp(self):
        self.currency = Currency.objects.create(code='INR', name='Indian Rupee', symbol='₹')
        self.company = CompanyProfile.objects.create(
            name='Test India Pvt Ltd',
            country='IN',
            fiscal_year_start_date=date(2023, 4, 1),
            default_currency=self.currency
        )
        # Assuming we can mock or set gstin_type on company if needed
        self.company.gstin_type = 'regular'
        
    def test_gst_due_dates(self):
        """Test generation of GST and TDS compliance deadlines"""
        calendar = IndiaComplianceCalendar(self.company)
        deadlines = calendar.get_deadlines(2023, 5) # May 2023
        
        # TDS for April is due May 7
        tds_deadline = next(d for d in deadlines if 'TDS Payment' in d['title'])
        self.assertEqual(tds_deadline['due_date'], date(2023, 5, 7))
        
        # GSTR-1 for April is due May 11
        gstr1_deadline = next(d for d in deadlines if 'GSTR-1' in d['title'])
        self.assertEqual(gstr1_deadline['due_date'], date(2023, 5, 11))
        
        # GSTR-3B for April is due May 20
        gstr3b_deadline = next(d for d in deadlines if 'GSTR-3B' in d['title'])
        self.assertEqual(gstr3b_deadline['due_date'], date(2023, 5, 20))
