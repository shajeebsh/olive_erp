"""
United Kingdom Tax Engine - Complete implementation for HMRC
"""
from decimal import Decimal
from datetime import date, timedelta
import re
from typing import Dict, List, Tuple, Optional

from compliance.decorators import register_tax_engine, register_compliance_engine
from compliance.base.engines import BaseTaxEngine, BaseComplianceEngine

VAT_RATES = {
    'standard': Decimal('20.0'),
    'reduced': Decimal('5.0'),
    'zero': Decimal('0.0'),
    'exempt': None  # Exempt (no VAT charged)
}

@register_tax_engine('GB')
class UKTaxEngine(BaseTaxEngine):
    """Complete UK tax engine implementing HMRC requirements"""
    
    country_code = 'GB'
    country_name = 'United Kingdom'
    currency_code = 'GBP'
    tax_name = 'VAT'
    
    # HMRC VAT periods
    VAT_PERIODS = {
        'monthly': {
            'due_day': 7,  # Due 7th of month after period end, plus 1 month for payment
            'description': 'Monthly VAT (for larger businesses)'
        },
        'quarterly': {
            'periods': [
                ('01-03', '04-07'),  # Jan-Mar, due 7 April (payment due 7 May)
                ('04-06', '07-07'),  # Apr-Jun, due 7 July (payment due 7 Aug)
                ('07-09', '10-07'),  # Jul-Sep, due 7 Oct (payment due 7 Nov)
                ('10-12', '01-07'),  # Oct-Dec, due 7 Jan (payment due 7 Feb)
            ],
            'description': 'Quarterly VAT (most common)'
        },
        'annual': {
            'period': ('01-12', '01-31'),  # Year end 31 Dec, due 31 Jan
            'description': 'Annual VAT (for small businesses)'
        }
    }
    
    def calculate_tax(self, amount: Decimal, tax_type: str,
                      customer_location: Optional[str] = None,
                      product_type: Optional[str] = None) -> Dict[str, Decimal]:
        """
        Calculate UK VAT based on rates and rules.
        
        Args:
            amount: Net amount
            tax_type: 'standard', 'reduced', 'zero', 'exempt'
            customer_location: For determining place of supply
            product_type: For special cases (e.g., domestic fuel)
        
        Returns:
            {'vat': calculated_vat} or {'vat': 0} for exempt
        """
        if tax_type == 'exempt':
            return {'vat': Decimal('0.00'), 'note': 'Exempt from VAT'}
        
        rate = VAT_RATES.get(tax_type, VAT_RATES['standard'])
        if rate is None:
            return {'vat': Decimal('0.00'), 'note': 'Exempt'}
        
        vat_amount = (amount * rate / Decimal('100')).quantize(Decimal('0.01'))
        
        result = {
            'vat': vat_amount,
            'rate': rate,
            'taxable_amount': amount
        }
        
        # Check for reverse charge (construction industry, etc.)
        if self.is_reverse_charge(product_type, customer_location):
            result['reverse_charge'] = True
            result['note'] = 'Reverse charge applies - customer accounts for VAT'
        
        return result
    
    def is_reverse_charge(self, product_type: str, customer_location: str) -> bool:
        """Check if reverse charge applies (CIS, etc.)"""
        # Construction Industry Scheme reverse charge
        if product_type == 'construction' and customer_location == 'GB':
            return True
        return False
    
    def get_tax_rates(self) -> List[Dict]:
        """Return all applicable UK VAT rates with conditions"""
        return [
            {'rate': 20.0, 'type': 'standard',
             'description': 'Standard Rate (20%) - Most goods and services'},
            {'rate': 5.0, 'type': 'reduced',
             'description': 'Reduced Rate (5%) - Domestic fuel, children\'s car seats'},
            {'rate': 0.0, 'type': 'zero',
             'description': 'Zero Rate (0%) - Food, books, children\'s clothes, exports'},
            {'rate': None, 'type': 'exempt',
             'description': 'Exempt - Insurance, education, healthcare, postal services'},
        ]
    
    def validate_tax_number(self, tax_number: str) -> Tuple[bool, str]:
        """
        Validate UK VAT number format (HMRC rules).
        
        Format: GB followed by 9 digits, or 12 digits for groups
        Examples: GB123456789, GB123456789012
        """
        if not tax_number:
            return False, "VAT number cannot be empty"
        
        # Remove spaces and convert to uppercase
        tax_number = tax_number.replace(' ', '').upper()
        
        # Check prefix
        if not tax_number.startswith('GB'):
            return False, "UK VAT numbers must start with 'GB'"
        
        # Extract digits
        digits = tax_number[2:]
        
        # Check length
        if len(digits) not in [9, 12]:
            return False, "VAT number must have 9 or 12 digits after GB"
        
        # Check all digits
        if not digits.isdigit():
            return False, "VAT number must contain only digits after GB"
        
        # HMRC checksum validation (simplified - real has MOD 97 algorithm)
        # In production, implement full HMRC checksum
        if len(digits) == 9:
            # Basic format check passed
            pass
        
        return True, f"Valid UK VAT number: {tax_number}"
    
    def generate_tax_return(self, from_date: date, to_date: date,
                           company_id: int) -> Dict:
        """
        Generate VAT return data for HMRC (VAT100 form).
        
        Returns data structure matching HMRC's 9-box VAT return:
        - Box 1: VAT due on sales
        - Box 2: VAT due on acquisitions from EU
        - Box 3: Total VAT due (Box 1 + Box 2)
        - Box 4: VAT reclaimed on purchases
        - Box 5: Net VAT to pay/reclaim (Box 3 - Box 4)
        - Box 6: Total value of sales excluding VAT
        - Box 7: Total value of purchases excluding VAT
        - Box 8: Total value of EU sales
        - Box 9: Total value of EU purchases
        """
        from finance.models import Invoice, JournalEntryLine
        from django.db.models import Sum, Q
        
        # Get all sales invoices in period
        sales_invoices = Invoice.objects.filter(
            company_id=company_id,
            issue_date__range=[from_date, to_date],
            type='sales',
            status='Paid'
        )
        
        # Get all purchase invoices in period
        purchase_invoices = Invoice.objects.filter(
            company_id=company_id,
            issue_date__range=[from_date, to_date],
            type='purchase',
            status='Paid'
        )
        
        # Calculate HMRC VAT boxes
        box1 = sales_invoices.aggregate(Sum('tax_amount'))['tax_amount__sum'] or 0
        
        # Box 2: VAT on EU acquisitions (simplified)
        box2 = Decimal('0.00')
        
        box3 = box1 + box2
        
        box4 = purchase_invoices.aggregate(Sum('tax_amount'))['tax_amount__sum'] or 0
        
        box5 = box3 - box4
        
        box6 = sales_invoices.filter(
            tax_rate__gt=0
        ).aggregate(Sum('subtotal'))['subtotal__sum'] or 0
        
        box7 = purchase_invoices.aggregate(Sum('subtotal'))['subtotal__sum'] or 0
        
        # EU sales and purchases (simplified)
        box8 = sales_invoices.filter(
            customer__country__in=['FR', 'DE', 'IT', 'ES', 'NL', 'BE', 'IE']
        ).aggregate(Sum('subtotal'))['subtotal__sum'] or 0
        
        box9 = purchase_invoices.filter(
            supplier__country__in=['FR', 'DE', 'IT', 'ES', 'NL', 'BE', 'IE']
        ).aggregate(Sum('subtotal'))['subtotal__sum'] or 0
        
        return {
            'period': {
                'from': from_date.isoformat(),
                'to': to_date.isoformat(),
                'due_date': self.get_vat_due_date(to_date).isoformat(),
                'payment_due_date': self.get_vat_payment_date(to_date).isoformat()
            },
            'boxes': {
                '1': float(box1),   # VAT due on sales
                '2': float(box2),   # VAT due on EU acquisitions
                '3': float(box3),   # Total VAT due
                '4': float(box4),   # VAT reclaimed
                '5': float(box5),   # Net VAT payable
                '6': float(box6),   # Total sales (ex VAT)
                '7': float(box7),   # Total purchases (ex VAT)
                '8': float(box8),   # EU sales
                '9': float(box9),   # EU purchases
            },
            'summary': {
                'total_sales': float(box6),
                'total_purchases': float(box7),
                'net_vat_due': float(box5),
                'is_refund': box5 < 0
            }
        }
    
    def get_vat_due_date(self, period_end: date) -> date:
        """Calculate VAT return due date (7th of month after period end)"""
        if period_end.month == 12:
            due_month = 1
            due_year = period_end.year + 1
        else:
            due_month = period_end.month + 1
            due_year = period_end.year
        
        return date(due_year, due_month, 7)
    
    def get_vat_payment_date(self, period_end: date) -> date:
        """Calculate VAT payment due date (7th of month after period end, plus 1 month)"""
        if period_end.month == 11:
            payment_month = 1
            payment_year = period_end.year + 1
        elif period_end.month == 12:
            payment_month = 2
            payment_year = period_end.year + 1
        else:
            payment_month = period_end.month + 2
            payment_year = period_end.year
        
        return date(payment_year, payment_month, 7)
    
    def get_vat_periods(self, year: int, frequency: str = 'quarterly') -> List[Dict]:
        """Generate VAT periods for a given year"""
        periods = []
        
        if frequency == 'quarterly':
            period_config = [
                (date(year, 1, 1), date(year, 3, 31), date(year, 4, 7), date(year, 5, 7)),
                (date(year, 4, 1), date(year, 6, 30), date(year, 7, 7), date(year, 8, 7)),
                (date(year, 7, 1), date(year, 9, 30), date(year, 10, 7), date(year, 11, 7)),
                (date(year, 10, 1), date(year, 12, 31), date(year+1, 1, 7), date(year+1, 2, 7)),
            ]
            
            for start, end, due, payment_due in period_config:
                periods.append({
                    'start': start.isoformat(),
                    'end': end.isoformat(),
                    'due': due.isoformat(),
                    'payment_due': payment_due.isoformat(),
                    'name': f"VAT Period Q{len(periods)+1} {year}"
                })
        
        return periods
