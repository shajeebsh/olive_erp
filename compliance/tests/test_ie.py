from django.test import TestCase
from decimal import Decimal
from datetime import date
from compliance.countries.ie import IrelandTaxEngine
from compliance.countries.ie.ct1 import CT1Calculator
from compliance.countries.ie.paye import PAYECalculator

class IrelandTaxEngineTests(TestCase):
    def setUp(self):
        self.engine = IrelandTaxEngine()
    
    def test_vat_calculation(self):
        result = self.engine.calculate_tax(Decimal('1000'), 'standard')
        self.assertEqual(result['vat'], Decimal('230.00'))
        self.assertEqual(result['rate'], Decimal('23.0'))
    
    def test_reduced_vat(self):
        result = self.engine.calculate_tax(Decimal('1000'), 'reduced')
        self.assertEqual(result['vat'], Decimal('135.00'))
    
    def test_livestock_vat(self):
        result = self.engine.calculate_tax(Decimal('1000'), 'livestock')
        self.assertEqual(result['vat'], Decimal('48.00'))
    
    def test_zero_rated(self):
        result = self.engine.calculate_tax(Decimal('1000'), 'zero')
        self.assertEqual(result['vat'], Decimal('0.00'))
    
    def test_exempt(self):
        result = self.engine.calculate_tax(Decimal('1000'), 'exempt')
        self.assertEqual(result['vat'], Decimal('0.00'))
        self.assertIn('note', result)
    
    def test_vat_number_validation(self):
        valid, msg = self.engine.validate_tax_number('IE1234567A')
        self.assertTrue(valid)
        
        valid, msg = self.engine.validate_tax_number('IE1234567')
        self.assertFalse(valid)
        
        valid, msg = self.engine.validate_tax_number('IE12345')
        self.assertFalse(valid)
        
        valid, msg = self.engine.validate_tax_number('GB123456789')
        self.assertFalse(valid)

class CT1CalculatorTests(TestCase):
    def setUp(self):
        # Setup test company and data
        pass
    
    def test_trading_income(self):
        # Test trading income calculation
        pass

class PAYECalculatorTests(TestCase):
    def setUp(self):
        # Setup test employee
        pass
    
    def test_paye_calculation(self):
        # Test PAYE calculation
        pass
