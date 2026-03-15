"""
Companies House API integration
"""
import requests
import base64
from typing import Dict, Any, List
from django.conf import settings

class CompaniesHouseAPI:
    """
    Companies House API client for filing and company information
    
    API documentation: https://developer.company-information.service.gov.uk/
    """
    
    BASE_URL = 'https://api.company-information.service.gov.uk'
    
    def __init__(self, company):
        self.company = company
        self.api_key = settings.COMPANIES_HOUSE_API_KEY if hasattr(settings, 'COMPANIES_HOUSE_API_KEY') else 'test-key'
        self.company_number = company.registration_number
        
    def get_headers(self):
        """Generate basic auth headers for Companies House API"""
        auth_string = base64.b64encode(f"{self.api_key}:".encode()).decode()
        return {
            'Authorization': f'Basic {auth_string}',
            'Content-Type': 'application/json'
        }
    
    def get_company_profile(self) -> Dict[str, Any]:
        """Get company details from Companies House"""
        # In production, make actual API call
        url = f"{self.BASE_URL}/company/{self.company_number}"
        
        # Mock response
        return {
            'company_name': self.company.name,
            'company_number': self.company_number,
            'company_status': 'active',
            'date_of_creation': '2020-01-01',
            'registered_office_address': {
                'address_line_1': self.company.address,
                'locality': 'London',
                'postal_code': 'SW1A 1AA',
                'country': 'United Kingdom'
            },
            'sic_codes': ['62020', '70229']
        }
    
    def get_officers(self) -> List[Dict]:
        """Get current officers"""
        url = f"{self.BASE_URL}/company/{self.company_number}/officers"
        
        # Mock response
        return [
            {
                'name': 'John Smith',
                'officer_role': 'director',
                'appointed_on': '2020-01-01',
                'nationality': 'British',
                'country_of_residence': 'England'
            }
        ]
    
    def get_pscs(self) -> List[Dict]:
        """Get Persons with Significant Control"""
        url = f"{self.BASE_URL}/company/{self.company_number}/persons-with-significant-control"
        
        # Mock response
        return [
            {
                'name': 'John Smith',
                'natures_of_control': ['ownership-of-shares-25-to-50-percent'],
                'notified_on': '2020-01-01'
            }
        ]
    
    def get_filing_history(self) -> List[Dict]:
        """Get filing history"""
        url = f"{self.BASE_URL}/company/{self.company_number}/filing-history"
        
        # Mock response
        return [
            {
                'category': 'accounts',
                'date': '2024-12-31',
                'description': 'micro-company accounts',
                'type': 'AA'
            }
        ]
    
    def submit_confirmation_statement(self, cs_data: Dict) -> Dict:
        """
        Submit CS01 confirmation statement
        In production, this would use the authenticated filing API
        """
        # Mock submission
        return {
            'transaction_id': f'CH{self.company_number}{cs_data["period_end"]}',
            'submitted_at': '2025-03-15T10:30:00Z',
            'status': 'accepted'
        }
    
    def validate_company_number(self, company_number: str) -> bool:
        """Validate UK company number format"""
        # Remove spaces
        company_number = company_number.replace(' ', '')
        
        # UK company numbers can be 8 digits, or 2 letters + 6 digits
        if company_number.isdigit() and len(company_number) == 8:
            return True
        elif len(company_number) == 8 and company_number[:2].isalpha() and company_number[2:].isdigit():
            return True
        elif company_number.startswith('SC') and len(company_number) == 8 and company_number[2:].isdigit():  # Scotland
            return True
        elif company_number.startswith('NI') and len(company_number) == 8 and company_number[2:].isdigit():  # N. Ireland
            return True
        elif company_number.startswith('OC') and len(company_number) == 8 and company_number[2:].isdigit():  # LLP
            return True
        
        return False
