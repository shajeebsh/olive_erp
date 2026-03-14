"""
United Kingdom country module - will be fully implemented in Phase 2C
"""
from compliance.decorators import register_tax_engine, register_compliance_engine
from compliance.base.engines import BaseTaxEngine, BaseComplianceEngine

@register_tax_engine('GB')
class UKTaxEngine(BaseTaxEngine):
    country_code = 'GB'
    country_name = 'United Kingdom'
    currency_code = 'GBP'
    tax_name = 'VAT'

    def calculate_tax(self, amount, tax_type, customer_location=None, product_type=None):
        rates = {'standard': 0.20, 'reduced': 0.05, 'zero': 0}
        return {'vat': amount * rates.get(tax_type, 0.20)}

    def get_tax_rates(self):
        return [
            {'rate': 20.0, 'type': 'standard', 'description': 'Standard Rate (20%)'},
            {'rate': 5.0, 'type': 'reduced', 'description': 'Reduced Rate (5%)'},
            {'rate': 0.0, 'type': 'zero', 'description': 'Zero Rate (0%)'},
        ]

    def validate_tax_number(self, tax_number):
        import re
        pattern = r'^GB\d{9}$|^GB\d{12}$'
        if re.match(pattern, tax_number):
            return True, "Valid UK VAT number"
        return False, "Invalid format. Should be GB followed by 9 or 12 digits"

    def generate_tax_return(self, from_date, to_date, company_id):
        return {'status': 'not_implemented', 'country': 'GB'}

@register_compliance_engine('GB')
class UKComplianceEngine(BaseComplianceEngine):
    country_code = 'GB'

    def get_filing_deadlines(self, company_id, year):
        return [
            {'form': 'CT600', 'name': 'Corporation Tax', 'due_date': f'{year}-12-31'},
            {'form': 'CS01', 'name': 'Confirmation Statement', 'due_date': f'{year}-01-31'},
        ]

    def generate_annual_return(self, company_id, year, filing_type):
        return {'status': 'not_implemented'}

    def validate_company_registration(self, registration_number):
        import re
        pattern = r'^[0-9]{8}$'
        if re.match(pattern, registration_number):
            return True, "Valid Companies House number"
        return False, "Invalid format. Should be 8 digits"
