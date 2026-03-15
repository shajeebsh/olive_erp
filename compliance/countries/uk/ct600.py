from decimal import Decimal
from datetime import date
from django.db.models import Sum, Q
from typing import Dict

class CT600Calculator:
    """
    Calculate UK Corporation Tax (CT600)
    
    Corporation Tax rates (2025):
    - 19% for profits below £50,000
    - 25% for profits above £250,000
    - Marginal relief between £50,000 and £250,000
    """
    
    # Corporation Tax rates and thresholds
    SMALL_PROFITS_RATE = Decimal('0.19')  # 19% for profits <= £50,000
    MAIN_RATE = Decimal('0.25')           # 25% for profits >= £250,000
    LOWER_LIMIT = Decimal('50000')        # £50,000
    UPPER_LIMIT = Decimal('250000')       # £250,000
    MARGINAL_RELIEF_FRACTION = Decimal('0.015')  # 3/200 for marginal relief calculation
    
    def __init__(self, company, accounting_period):
        self.company = company
        self.period = accounting_period
        self.profits = {
            'trading': Decimal('0.00'),
            'property': Decimal('0.00'),
            'interest': Decimal('0.00'),
            'chargeable_gains': Decimal('0.00'),
            'other': Decimal('0.00')
        }
        self.deductions = {
            'trading_losses_brought_forward': Decimal('0.00'),
            'property_losses_brought_forward': Decimal('0.00'),
            'capital_allowances': Decimal('0.00'),
            'trading_losses_relieved': Decimal('0.00'),
            'non_trading_loan_relationship_deficits': Decimal('0.00'),
            'management_expenses': Decimal('0.00')
        }
        self.reliefs = {
            'patent_box': Decimal('0.00'),
            'creative_industry': Decimal('0.00'),
            'research_development': Decimal('0.00')
        }
    
    def calculate_trading_income(self):
        """Calculate trading income (adjusted for tax)"""
        from finance.models import JournalEntryLine, Account
        
        # Get trading income accounts
        trading_accounts = Account.objects.filter(
            company=self.company,
            name__icontains='trading',
            account_type='Income'
        )
        
        # Sum credits to these accounts
        income = JournalEntryLine.objects.filter(
            account__in=trading_accounts,
            journal_entry__date__range=[self.period.start, self.period.end],
            journal_entry__is_posted=True
        ).aggregate(total=Sum('credit'))['total'] or 0
        
        # Less allowable expenses
        expense_accounts = Account.objects.filter(
            company=self.company,
            account_type='Expense',
            name__in=['Rent', 'Rates', 'Utilities', 'Salaries', 'Professional Fees']
        )
        
        expenses = JournalEntryLine.objects.filter(
            account__in=expense_accounts,
            journal_entry__date__range=[self.period.start, self.period.end],
            journal_entry__is_posted=True
        ).aggregate(total=Sum('debit'))['total'] or 0
        
        self.profits['trading'] = income - expenses
        return self.profits['trading']
    
    def calculate_property_income(self):
        """Calculate property income"""
        from finance.models import JournalEntryLine, Account
        
        property_accounts = Account.objects.filter(
            company=self.company,
            name__in=['Rental Income', 'Property Income']
        )
        
        income = JournalEntryLine.objects.filter(
            account__in=property_accounts,
            journal_entry__date__range=[self.period.start, self.period.end]
        ).aggregate(total=Sum('credit'))['total'] or 0
        
        # Property expenses
        property_expense_accounts = Account.objects.filter(
            company=self.company,
            name__in=['Property Repairs', 'Property Insurance', 'Property Management Fees']
        )
        
        expenses = JournalEntryLine.objects.filter(
            account__in=property_expense_accounts,
            journal_entry__date__range=[self.period.start, self.period.end]
        ).aggregate(total=Sum('debit'))['total'] or 0
        
        self.profits['property'] = income - expenses
        return self.profits['property']
    
    def calculate_interest_income(self):
        """Calculate interest and other non-trading income"""
        from finance.models import JournalEntryLine, Account
        
        interest_accounts = Account.objects.filter(
            company=self.company,
            name__in=['Interest Received', 'Bank Interest', 'Loan Interest']
        )
        
        self.profits['interest'] = JournalEntryLine.objects.filter(
            account__in=interest_accounts,
            journal_entry__date__range=[self.period.start, self.period.end]
        ).aggregate(total=Sum('credit'))['total'] or 0
        
        return self.profits['interest']
    
    def calculate_chargeable_gains(self):
        """Calculate chargeable gains (from asset disposals)"""
        from inventory.models import AssetDisposal
        
        disposals = AssetDisposal.objects.filter(
            company=self.company,
            disposal_date__range=[self.period.start, self.period.end]
        )
        
        total_gains = Decimal('0.00')
        for disposal in disposals:
            gain = disposal.proceeds - disposal.cost - disposal.incidental_costs
            if gain > 0:
                total_gains += gain
        
        self.profits['chargeable_gains'] = total_gains
        return total_gains
    
    def calculate_total_profits(self) -> Decimal:
        """Calculate total profits before reliefs"""
        # Ensure all components are calculated
        self.calculate_trading_income()
        self.calculate_property_income()
        self.calculate_interest_income()
        self.calculate_chargeable_gains()
        
        total = sum(self.profits.values())
        return total
    
    def apply_loss_relief(self, total_profits: Decimal) -> Decimal:
        """Apply loss relief (simplified)"""
        from finance.models import TaxLoss
        
        # Get brought forward trading losses
        losses = TaxLoss.objects.filter(
            company=self.company,
            utilized=False,
            type='trading'
        ).order_by('year')
        
        for loss in losses:
            if total_profits <= 0:
                break
            
            available = loss.amount - loss.utilized_amount
            if available > 0:
                used = min(available, total_profits)
                self.deductions['trading_losses_relieved'] += used
                total_profits -= used
                
                # Update loss utilization
                loss.utilized_amount += used
                if loss.utilized_amount >= loss.amount:
                    loss.utilized = True
                loss.save()
        
        return total_profits
    
    def calculate_capital_allowances(self) -> Decimal:
        """Calculate capital allowances (simplified)"""
        from inventory.models import Asset
        
        # Annual Investment Allowance (AIA) - 100% on first £200,000
        assets = Asset.objects.filter(
            company=self.company,
            purchase_date__range=[self.period.start, self.period.end]
        )
        
        total_cost = assets.aggregate(total=Sum('cost'))['total'] or 0
        aia = min(total_cost, Decimal('200000'))
        
        # Writing Down Allowance (WDA) - 18% on remaining pool
        existing_assets = Asset.objects.filter(
            company=self.company,
            purchase_date__lt=self.period.start
        )
        
        pool_value = existing_assets.aggregate(total=Sum('tax_written_down_value'))['total'] or 0
        wda = pool_value * Decimal('0.18')
        
        self.deductions['capital_allowances'] = aia + wda
        return self.deductions['capital_allowances']
    
    def calculate_tax(self) -> Dict:
        """Complete CT600 calculation"""
        # Calculate total profits
        total_profits = self.calculate_total_profits()
        
        # Apply capital allowances
        capital_allowances = self.calculate_capital_allowances()
        total_profits -= capital_allowances
        
        # Apply loss relief
        profits_after_losses = self.apply_loss_relief(total_profits)
        
        # Calculate tax based on profit level
        if profits_after_losses <= self.LOWER_LIMIT:
            # Small profits rate
            tax = profits_after_losses * self.SMALL_PROFITS_RATE
            marginal_relief = Decimal('0.00')
            effective_rate = self.SMALL_PROFITS_RATE
        elif profits_after_losses >= self.UPPER_LIMIT:
            # Main rate
            tax = profits_after_losses * self.MAIN_RATE
            marginal_relief = Decimal('0.00')
            effective_rate = self.MAIN_RATE
        else:
            # Marginal relief
            tax_at_main_rate = profits_after_losses * self.MAIN_RATE
            marginal_relief_fraction = (self.UPPER_LIMIT - profits_after_losses) / self.UPPER_LIMIT
            marginal_relief = tax_at_main_rate * marginal_relief_fraction * self.MARGINAL_RELIEF_FRACTION
            tax = tax_at_main_rate - marginal_relief
            effective_rate = tax / profits_after_losses
        
        return {
            'profits': {
                'trading': float(self.profits['trading']),
                'property': float(self.profits['property']),
                'interest': float(self.profits['interest']),
                'chargeable_gains': float(self.profits['chargeable_gains']),
                'total': float(total_profits + capital_allowances)
            },
            'deductions': {
                'capital_allowances': float(capital_allowances),
                'losses_relieved': float(self.deductions['trading_losses_relieved'])
            },
            'taxable_profits': float(profits_after_losses),
            'tax_calculation': {
                'tax_due': float(tax),
                'marginal_relief': float(marginal_relief),
                'effective_rate': float(effective_rate),
                'main_rate_applicable': profits_after_losses >= self.UPPER_LIMIT,
                'small_profits_rate_applicable': profits_after_losses <= self.LOWER_LIMIT
            }
        }
