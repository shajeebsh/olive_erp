from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import date, datetime

class BaseTaxEngine(ABC):
    """
    Abstract base class for all country tax engines.
    All country implementations MUST inherit from this.
    """

    @property
    @abstractmethod
    def country_code(self) -> str:
        """ISO country code (e.g., 'IE', 'GB', 'IN', 'AE')"""
        pass

    @property
    @abstractmethod
    def country_name(self) -> str:
        """Full country name"""
        pass

    @property
    @abstractmethod
    def currency_code(self) -> str:
        """ISO currency code (e.g., 'EUR', 'GBP', 'INR', 'AED')"""
        pass

    @property
    @abstractmethod
    def tax_name(self) -> str:
        """Name of tax (e.g., 'VAT', 'GST', 'Sales Tax')"""
        pass

    @abstractmethod
    def calculate_tax(self, amount: Decimal, tax_type: str,
                        customer_location: Optional[str] = None,
                        product_type: Optional[str] = None) -> Dict[str, Decimal]:
        """
        Calculate tax based on country rules.
        Returns dict with tax components (e.g., {'cgst': 9.0, 'sgst': 9.0})
        """
        pass

    @abstractmethod
    def get_tax_rates(self) -> List[Dict]:
        """Return applicable tax rates with conditions"""
        pass

    @abstractmethod
    def validate_tax_number(self, tax_number: str) -> Tuple[bool, str]:
        """
        Validate country-specific tax ID format.
        Returns (is_valid, message)
        """
        pass

    @abstractmethod
    def generate_tax_return(self, from_date: date, to_date: date,
                              company_id: int) -> Dict:
        """Generate country-specific tax return data"""
        pass

    def get_withholding_tax(self, amount: Decimal, supplier_type: str,
                              transaction_type: str) -> Decimal:
        """
        Calculate withholding tax if applicable.
        Default implementation returns 0 - override if needed.
        """
        return Decimal('0.00')

    def get_reverse_charge(self, amount: Decimal, supplier_country: str,
                             service_type: str) -> Dict:
        """
        Calculate reverse charge if applicable.
        Default implementation returns empty - override if needed.
        """
        return {}


class BaseComplianceEngine(ABC):
    """
    Abstract base for statutory compliance (annual returns, registrations)
    """

    @property
    @abstractmethod
    def country_code(self) -> str:
        pass

    @abstractmethod
    def get_filing_deadlines(self, company_id: int, year: int) -> List[Dict]:
        """
        Return all filing deadlines for the year
        """
        pass

    @abstractmethod
    def generate_annual_return(self, company_id: int, year: int,
                                 filing_type: str) -> Dict:
        """
        Generate annual return data (e.g., CRO B1, Companies House)
        """
        pass

    @abstractmethod
    def validate_company_registration(self, registration_number: str) -> Tuple[bool, str]:
        """Validate company registration number format"""
        pass

    def get_forms(self) -> List[Dict]:
        """Return available statutory forms for this country"""
        return []
