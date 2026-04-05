from decimal import Decimal
from datetime import date
from django.db.models import Sum

class TDSCalculator:
    """
    Service for calculating Indian TDS on vendor payments.
    """
    
    def __init__(self, company):
        self.company = company
        
    def check_threshold(self, vendor, section, current_bill_amount: Decimal, bill_date: date) -> bool:
        """
        Check if TDS should be deducted based on single bill and aggregate thresholds.
        
        Args:
            vendor: Supplier instance
            section: TDSSection instance
            current_bill_amount: Amount of the current bill
            bill_date: Date of the bill (to determine financial year)
        """
        if not section.threshold_limit_single and not section.threshold_limit_aggregate:
            return True # No threshold, always deduct
            
        # Check single bill threshold
        if section.threshold_limit_single and current_bill_amount >= section.threshold_limit_single:
            return True
            
        # Check aggregate threshold for financial year
        if section.threshold_limit_aggregate:
            # Determine Financial Year boundaries (Apr 1 to Mar 31)
            if bill_date.month >= 4:
                fy_start = date(bill_date.year, 4, 1)
                fy_end = date(bill_date.year + 1, 3, 31)
            else:
                fy_start = date(bill_date.year - 1, 4, 1)
                fy_end = date(bill_date.year, 3, 31)
                
            from finance.models import Invoice
            # Sum of previous bills in this financial year for this vendor
            previous_total = Invoice.objects.filter(
                supplier=vendor,
                type='purchase',
                issue_date__gte=fy_start,
                issue_date__lte=fy_end
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            
            if (previous_total + current_bill_amount) >= section.threshold_limit_aggregate:
                return True
                
        return False
        
    def calculate_tds(self, vendor, section_code: str, amount: Decimal, bill_date: date) -> dict:
        """
        Calculate TDS amount for a given bill.
        
        Args:
            vendor: Supplier instance
            section_code: e.g., '194C'
            amount: Bill base amount
            bill_date: Date of bill
            
        Returns:
            Dict containing TDS details or None if not applicable
        """
        from .tds import TDSSection
        
        # Determine vendor party type
        # In a real app, Supplier model would have a 'tax_entity_type' field
        # We simplify here checking if name has "Ltd" or "Pvt"
        party_type = 'company' if any(x in vendor.name.lower() for x in ['ltd', 'limited', 'pvt']) else 'non_company'
        
        try:
            section = TDSSection.objects.get(
                tenant=self.company.tenant,
                section_code=section_code,
                party_type=party_type
            )
        except TDSSection.DoesNotExist:
            return None # Section not configured
            
        # Check if PAN is available (if not, highest rate of 20% applies usually)
        if not vendor.tax_number: # Assume tax_number stores PAN if no GSTIN
            effective_rate = Decimal('20.00')
        else:
            effective_rate = section.rate_percent
            
        # Check thresholds
        if not self.check_threshold(vendor, section, amount, bill_date):
            return {
                'deduct': False,
                'reason': 'Below threshold limits'
            }
            
        # Calculate TDS
        tds_amount = (amount * effective_rate / Decimal('100')).quantize(Decimal('0.01'))
        
        return {
            'deduct': True,
            'section': section,
            'rate': effective_rate,
            'base_amount': amount,
            'tds_amount': tds_amount
        }
