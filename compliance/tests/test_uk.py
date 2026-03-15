from django.test import TestCase
from decimal import Decimal
from datetime import date
from compliance.countries.uk import UKTaxEngine
from compliance.countries.uk.ct600 import CT600Calculator
from compliance.countries.uk.rti import RTICalculator

class UKTaxEngineTests(TestCase):
    def setUp(self):
        self.engine = UKTaxEngine()
    
    def test_vat_calculation(self):
        result = self.engine.calculate_tax(Decimal('1000'), 'standard')
        self.assertEqual(result['vat'], Decimal('200.00'))
        self.assertEqual(result['rate'], Decimal('20.0'))
    
    def test_reduced_vat(self):
        result = self.engine.calculate_tax(Decimal('1000'), 'reduced')
        self.assertEqual(result['vat'], Decimal('50.00'))
    
    def test_zero_rated(self):
        result = self.engine.calculate_tax(Decimal('1000'), 'zero')
        self.assertEqual(result['vat'], Decimal('0.00'))
    
    def test_exempt(self):
        result = self.engine.calculate_tax(Decimal('1000'), 'exempt')
        self.assertEqual(result['vat'], Decimal('0.00'))
        self.assertIn('note', result)
    
    def test_vat_number_validation(self):
        valid, msg = self.engine.validate_tax_number('GB123456789')
        self.assertTrue(valid)
        
        valid, msg = self.engine.validate_tax_number('GB123456789012')
        self.assertTrue(valid)
        
        valid, msg = self.engine.validate_tax_number('GB12345')
        self.assertFalse(valid)
        
        valid, msg = self.engine.validate_tax_number('IE1234567A')
        self.assertFalse(valid)

class RTICalculatorTests(TestCase):
    def setUp(self):
        # Setup test employee
        pass
    
    def test_tax_calculation_basic_rate(self):
        # Test PAYE calculation at basic rate
        pass
    
    def test_ni_calculation(self):
        # Test NI calculation
        pass

class CT600CalculatorTests(TestCase):
    def setUp(self):
        # Setup test company
        pass
    
    def test_small_profits_rate(self):
        # Test 19% rate
        pass
    
    def test_main_rate(self):
        # Test 25% rate
        pass
