"""
Corporate Tax calculation engine
"""
from decimal import Decimal
from typing import Dict, Optional

class CorporateTaxCalculator:
    """
    Calculate UAE Corporate Tax
    """
    
    SMALL_BUSINESS_THRESHOLD = Decimal('375000')
    CORPORATE_TAX_RATE = Decimal('9.0')
    
    def __init__(self, company, tax_period):
        self.company = company
        self.tax_period = tax_period
    
    def calculate_taxable_income(self, financial_data: Dict) -> Decimal:
        """
        Calculate taxable income from financial data
        
        Args:
            financial_data: Dict with revenue, expenses, etc.
        """
        revenue = financial_data.get('revenue', Decimal('0.00'))
        cogs = financial_data.get('cost_of_goods_sold', Decimal('0.00'))
        operating_expenses = financial_data.get('operating_expenses', Decimal('0.00'))
        other_income = financial_data.get('other_income', Decimal('0.00'))
        other_expenses = financial_data.get('other_expenses', Decimal('0.00'))
        
        # Basic P&L
        gross_profit = revenue - cogs
        net_profit = gross_profit - operating_expenses + other_income - other_expenses
        
        # Adjustments
        non_deductible = financial_data.get('non_deductible_expenses', Decimal('0.00'))
        exempt_income = financial_data.get('exempt_income', Decimal('0.00'))
        
        taxable_income = net_profit + non_deductible - exempt_income
        
        return taxable_income.quantize(Decimal('0.01'))
    
    def apply_loss_relief(self, taxable_income: Decimal) -> Decimal:
        """Apply carried forward losses (max 75% of taxable income)"""
        from django.db import models
        from .corporate_tax import TaxLoss
        
        losses = TaxLoss.objects.filter(
            company=self.company,
            is_active=True
        ).exclude(loss_amount__lte=models.F('utilized_amount'))
        
        total_losses_available = sum(
            (loss.loss_amount - loss.utilized_amount)
            for loss in losses
        )
        
        # Loss relief limited to 75% of taxable income
        max_loss_relief = taxable_income * Decimal('0.75')
        loss_to_apply = min(total_losses_available, max_loss_relief)
        
        # Apply losses (FIFO order)
        remaining_to_apply = loss_to_apply
        for loss in losses.order_by('loss_year'):
            available = loss.loss_amount - loss.utilized_amount
            if available <= 0:
                continue
            
            apply_now = min(available, remaining_to_apply)
            loss.utilized_amount += apply_now
            loss.save()
            
            remaining_to_apply -= apply_now
            if remaining_to_apply <= 0:
                break
        
        return taxable_income - loss_to_apply
    
    def check_small_business_relief(self, revenue: Decimal) -> bool:
        """Check if eligible for small business relief"""
        # Small business relief: revenue ≤ AED 3,000,000 (from 2024)
        # Threshold may change - check current FTA guidance
        return revenue <= Decimal('3000000')
    
    def calculate_tax(self, financial_data: Dict) -> Dict:
        """
        Complete corporate tax calculation
        """
        from .corporate_tax import FreeZonePerson
        
        # Calculate taxable income
        taxable_income = self.calculate_taxable_income(financial_data)
        
        # Apply loss relief
        income_after_losses = self.apply_loss_relief(taxable_income)
        
        # Check if Free Zone Person
        try:
            fz_person = FreeZonePerson.objects.get(company=self.company)
            is_free_zone = True
            
            # Qualifying income calculation
            qualifying = financial_data.get('qualifying_income', Decimal('0.00'))
            non_qualifying = financial_data.get('non_qualifying_income', Decimal('0.00'))
            total_revenue = qualifying + non_qualifying
            
            # Check de minimis
            de_minimis_ok = fz_person.check_de_minimis(total_revenue)
            
            # Free Zone person pays 0% on qualifying income
            # 9% on non-qualifying income (if above de minimis)
            if de_minimis_ok:
                tax_qualifying = Decimal('0.00')
                tax_non_qualifying = Decimal('0.00')
            else:
                # Excess non-qualifying income taxed at 9%
                excess = non_qualifying - min(non_qualifying, Decimal('5000000'))
                excess_percent = (non_qualifying / total_revenue * 100) if total_revenue > 0 else 0
                if excess_percent > 5:
                    # All non-qualifying income taxed
                    tax_non_qualifying = non_qualifying * self.CORPORATE_TAX_RATE / Decimal('100')
                else:
                    tax_non_qualifying = Decimal('0.00')
                tax_qualifying = Decimal('0.00')
            
            total_tax = tax_qualifying + tax_non_qualifying
            
        except FreeZonePerson.DoesNotExist:
            is_free_zone = False
            
            # Check small business relief (Revenue <= 3M)
            small_business = self.check_small_business_relief(financial_data.get('revenue', Decimal('0.0')))
            
            if small_business and income_after_losses <= self.SMALL_BUSINESS_THRESHOLD:
               # Full relief
               total_tax = Decimal('0.00')
               effective_rate = 0
            else:
               # 0% on first AED 375,000, 9% on excess
               if income_after_losses <= self.SMALL_BUSINESS_THRESHOLD:
                   total_tax = Decimal('0.00')
                   effective_rate = 0
               else:
                   taxable_above = income_after_losses - self.SMALL_BUSINESS_THRESHOLD
                   total_tax = taxable_above * self.CORPORATE_TAX_RATE / Decimal('100')
                   effective_rate = (total_tax / income_after_losses * 100) if income_after_losses > 0 else 0
        
        return {
            'financials': {
                'revenue': float(financial_data.get('revenue', 0)),
                'gross_profit': float(financial_data.get('revenue', 0) - financial_data.get('cost_of_goods_sold', 0)),
                'net_profit_before_tax': float(taxable_income),
                'adjustments': float(financial_data.get('non_deductible_expenses', 0) - financial_data.get('exempt_income', 0)),
            },
            'taxable_income': float(income_after_losses),
            'losses_utilized': float(taxable_income - income_after_losses),
            'tax_calculation': {
                'is_free_zone': is_free_zone,
                'small_business_relief': not is_free_zone and self.check_small_business_relief(financial_data.get('revenue', Decimal('0.0'))),
                'tax_rate': 0 if is_free_zone else 9.0,
                'tax_amount': float(total_tax.quantize(Decimal('0.01'))),
                'effective_rate': float(effective_rate) if not is_free_zone else 0,
            }
        }
