from django.test import TestCase
from decimal import Decimal
from datetime import date
from compliance.countries.ae import UAETaxEngine
from compliance.countries.ae.excise import ExciseGoodsCategory, ExciseProduct
from compliance.countries.ae.excise_calculator import ExciseCalculator
from compliance.countries.ae.corporate_tax import TaxLoss, CorporateTaxReturn, FreeZonePerson
from compliance.countries.ae.corporate_calculator import CorporateTaxCalculator
from compliance.countries.ae.calendar import UAEComplianceCalendar
from compliance.countries.ae.fta_client import FTAClient
from company.models import CompanyProfile, Currency

class UAETaxEngineTests(TestCase):
    def setUp(self):
        self.engine = UAETaxEngine()
        currency, _ = Currency.objects.get_or_create(code='AED', name='Dirham', symbol='AED')
        self.company = CompanyProfile.objects.create(
            name='UAE Test Company',
            tax_id='300123456789012',
            default_currency=currency,
            country='AE',
            fiscal_year_start_date=date(2025, 1, 1)
        )
        
    def test_vat_computation(self):
        # 5% standard
        res_standard = self.engine.calculate_tax(Decimal('100.00'), 'standard')
        self.assertEqual(res_standard['vat'], Decimal('5.00'))
        
        # 0% zero rate
        res_zero = self.engine.calculate_tax(Decimal('100.00'), 'zero')
        self.assertEqual(res_zero['vat'], Decimal('0.00'))
        
        # Exempt
        res_exempt = self.engine.calculate_tax(Decimal('100.00'), 'exempt')
        self.assertEqual(res_exempt['vat'], Decimal('0.00'))
        
    def test_trn_validation(self):
        valid, msg = self.engine.validate_tax_number('300123456789012')
        self.assertTrue(valid)
        
        invalid, msg = self.engine.validate_tax_number('12345')
        self.assertFalse(invalid)

class UAEExciseTests(TestCase):
    def setUp(self):
        self.engine = UAETaxEngine()

    def test_excise_computation(self):
        # Tobacco 100%
        res_tobacco = self.engine.calculate_excise(Decimal('50.00'), 'tobacco')
        self.assertEqual(res_tobacco['excise_amount'], Decimal('50.00'))
        self.assertEqual(res_tobacco['total_with_excise'], 100.0)
        
        # Carbonated Drinks 50%
        res_carb = self.engine.calculate_excise(Decimal('10.00'), 'carbonated', quantity=Decimal('2'))
        self.assertEqual(res_carb['excise_amount'], Decimal('10.00'))
        self.assertEqual(res_carb['total_with_excise'], 30.0)

class UAECorporateTaxTests(TestCase):
    def setUp(self):
        currency, _ = Currency.objects.get_or_create(code='AED')
        self.company = CompanyProfile.objects.create(
            name='UAE CT Company', 
            default_currency=currency,
            fiscal_year_start_date=date(2025, 1, 1)
        )
        self.calc = CorporateTaxCalculator(self.company, '2025Q1')

    def test_corporate_tax_standard(self):
        # Below threshold
        data_below = {'revenue': Decimal('300000')}
        res = self.calc.calculate_tax(data_below)
        self.assertEqual(res['tax_calculation']['tax_amount'], 0.0)
        
        # Above threshold
        data_above = {'revenue': Decimal('5000000')} # Large revenue
        res_above = self.calc.calculate_tax(data_above)
        # Assuming no expenses, profit = 5000000
        tax = (Decimal('5000000') - Decimal('375000')) * Decimal('0.09')
        self.assertAlmostEqual(res_above['tax_calculation']['tax_amount'], float(tax))

    def test_loss_relief(self):
        TaxLoss.objects.create(company=self.company, loss_year=2024, loss_amount=Decimal('500000'))
        
        data = {'revenue': Decimal('100000')}
        # Taxable income = 100000. Relief limited to 75% = 75000.
        res = self.calc.calculate_tax(data)
        self.assertEqual(res['taxable_income'], 25000.0)

class UAEFreeZoneTests(TestCase):
    def setUp(self):
        currency, _ = Currency.objects.get_or_create(code='AED')
        self.company = CompanyProfile.objects.create(
            name='FZ Company', 
            default_currency=currency,
            fiscal_year_start_date=date(2025, 1, 1)
        )
        self.fz_person = FreeZonePerson.objects.create(
            company=self.company,
            free_zone_name='dmcc',
            license_issue_date=date(2020, 1, 1),
            license_expiry_date=date(2030, 1, 1)
        )
        self.calc = CorporateTaxCalculator(self.company, '2025')

    def test_free_zone_tax(self):
        data = {
            'qualifying_income': Decimal('1000000'),
            'non_qualifying_income': Decimal('100000') # Below de minimis 5% of 1.1M is 55000, wait, it's < 5M and < 5%? No, 100k > 55k, so over 5%. Wait, De minimis logic: percent <= 5% or amount <= 5M. 100k <= 5M, so de minimis should be True.
        }
        res = self.calc.calculate_tax(data)
        self.assertEqual(res['tax_calculation']['tax_amount'], 0.0)

class FTAClientTests(TestCase):
    def setUp(self):
        currency, _ = Currency.objects.get_or_create(code='AED')
        self.company = CompanyProfile.objects.create(
            name='FTA Client', 
            tax_id='300123456789012', 
            default_currency=currency,
            fiscal_year_start_date=date(2025, 1, 1)
        )
        self.client = FTAClient(self.company)

    def test_file_vat_return(self):
        res = self.client.file_vat_return({})
        self.assertTrue(res['success'])
        self.assertIn('submission_id', res)

class UAECalendarTests(TestCase):
    def setUp(self):
        currency, _ = Currency.objects.get_or_create(code='AED')
        self.company = CompanyProfile.objects.create(
            name='Calendar Co', 
            default_currency=currency,
            fiscal_year_start_date=date(2025, 1, 1)
        )
        self.calendar = UAEComplianceCalendar(self.company, 2025)

    def test_get_deadlines(self):
        deadlines = self.calendar.get_all_deadlines()
        self.assertTrue(len(deadlines) > 0)
        vat_deadlines = [d for d in deadlines if d.form == 'VAT201']
        self.assertEqual(len(vat_deadlines), 4) # Quarterly
        
        excise_deadlines = [d for d in deadlines if d.form == 'Excise Declaration']
        self.assertEqual(len(excise_deadlines), 12) # Monthly
