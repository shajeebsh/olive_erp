"""
CT1 Corporation Tax computation engine
"""
from decimal import Decimal
from datetime import date
from django.db.models import Sum, Q

class CT1Calculator:
    """Calculate Irish Corporation Tax (CT1)"""
    
    # Corporation Tax rates
    RATES = {
        'trading': Decimal('0.125'),  # 12.5% trading income
        'passive': Decimal('0.25'),   # 25% passive income
        'capital_gains': Decimal('0.33'),  # 33% capital gains
    }
    
    # Close company surcharge
    CLOSE_COMPANY_SURCHARGE = Decimal('0.20')  # 20% on undistributed estate income
    
    def __init__(self, company, accounting_period):
        self.company = company
        self.period = accounting_period
        self.taxable_income = Decimal('0.00')
        self.charges = []
        
    def calculate_trading_income(self):
        """Calculate trading income (Schedule D Case I/II)"""
        from finance.models import JournalEntryLine, Account
        
        # Get all trading income accounts
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
        
        return income
    
    def calculate_passive_income(self):
        """Calculate passive income (rent, royalties, interest)"""
        from finance.models import JournalEntryLine, Account
        
        passive_accounts = Account.objects.filter(
            company=self.company,
            name__in=['Rental Income', 'Interest Received', 'Royalties'],
            account_type='Income'
        )
        
        income = JournalEntryLine.objects.filter(
            account__in=passive_accounts,
            journal_entry__date__range=[self.period.start, self.period.end],
            journal_entry__is_posted=True
        ).aggregate(total=Sum('credit'))['total'] or 0
        
        return income
    
    def calculate_capital_allowances(self):
        """Calculate capital allowances (accelerated for certain assets)"""
        from inventory.models import Asset
        
        assets = Asset.objects.filter(
            company=self.company,
            purchase_date__lte=self.period.end
        )
        
        total_allowances = Decimal('0.00')
        for asset in assets:
            # Different rates for different asset types
            if asset.asset_type in ['computer', 'software']:
                # 100% accelerated allowance for computers
                allowance = asset.cost
            elif asset.asset_type in ['plant', 'machinery']:
                # 12.5% per year
                allowance = asset.cost * Decimal('0.125')
            elif asset.asset_type == 'motor_vehicle':
                # Based on CO2 emissions
                if asset.co2_emissions and asset.co2_emissions < 155:
                    allowance = asset.cost * Decimal('0.125')
                else:
                    allowance = min(asset.cost, Decimal('24000')) * Decimal('0.125')
            else:
                allowance = Decimal('0.00')
            
            total_allowances += allowance
        
        return total_allowances
    
    def calculate_loss_relief(self):
        """Calculate loss relief options"""
        from finance.models import TaxLoss
        
        losses = TaxLoss.objects.filter(
            company=self.company,
            utilized=False
        ).order_by('year')
        
        relief = {
            'current_year': Decimal('0.00'),
            'carry_forward': Decimal('0.00'),
            'carry_back': Decimal('0.00')
        }
        
        # Current year loss
        if self.taxable_income < 0:
            relief['current_year'] = abs(self.taxable_income)
        
        # Carry forward losses from previous years
        for loss in losses:
            if loss.year < self.period.start.year:
                remaining = loss.amount - loss.utilized_amount
                if remaining > 0:
                    relief['carry_forward'] += remaining
        
        return relief
    
    def compute_ct1(self):
        """Complete CT1 computation"""
        trading_income = self.calculate_trading_income()
        passive_income = self.calculate_passive_income()
        
        # Deductible expenses
        from finance.models import Expense
        expenses = Expense.objects.filter(
            company=self.company,
            date__range=[self.period.start, self.period.end],
            is_deductible=True
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Capital allowances
        capital_allowances = self.calculate_capital_allowances()
        
        # Case I (trading) computation
        case_i_profit = trading_income - expenses - capital_allowances
        
        # Case III/IV/V (passive) computation
        case_iii_profit = passive_income
        
        # Loss relief
        losses = self.calculate_loss_relief()
        
        # Apply loss relief
        if case_i_profit > 0 and losses['carry_forward'] > 0:
            loss_used = min(case_i_profit, losses['carry_forward'])
            case_i_profit -= loss_used
        
        # Calculate tax
        tax_case_i = case_i_profit * self.RATES['trading'] if case_i_profit > 0 else 0
        tax_case_iii = case_iii_profit * self.RATES['passive'] if case_iii_profit > 0 else 0
        
        total_tax = tax_case_i + tax_case_iii
        
        # Close company surcharge (if applicable)
        surcharge = Decimal('0.00')
        if self.is_close_company():
            # Surcharge on undistributed estate income
            estate_income = self.get_estate_income()
            if estate_income > 0:
                surcharge = estate_income * self.CLOSE_COMPANY_SURCHARGE
        
        return {
            'income': {
                'trading': float(trading_income),
                'passive': float(passive_income),
                'total': float(trading_income + passive_income)
            },
            'deductions': {
                'expenses': float(expenses),
                'capital_allowances': float(capital_allowances),
                'total_deductions': float(expenses + capital_allowances)
            },
            'profits': {
                'case_i': float(case_i_profit),
                'case_iii': float(case_iii_profit),
                'total_profits': float(case_i_profit + case_iii_profit)
            },
            'losses': {
                'carry_forward': float(losses['carry_forward']),
                'utilized_this_year': float(loss_used) if 'loss_used' in locals() else 0
            },
            'tax': {
                'case_i_tax': float(tax_case_i),
                'case_iii_tax': float(tax_case_iii),
                'total_tax': float(total_tax),
                'surcharge': float(surcharge),
                'tax_due': float(total_tax + surcharge)
            }
        }
    
    def is_close_company(self):
        """Determine if company is a close company"""
        # Check if controlled by 5 or fewer participators
        from .models import Shareholder
        shareholders = Shareholder.objects.filter(company=self.company)
        
        if shareholders.count() <= 5:
            return True
        
        # Check if directors control >50%
        director_control = 0
        for shareholder in shareholders:
            if shareholder.is_director:
                director_control += shareholder.percentage_held
        
        return director_control > 50
    
    def get_estate_income(self):
        """Get estate and investment income for surcharge calculation"""
        from finance.models import JournalEntryLine, Account
        
        estate_accounts = Account.objects.filter(
            company=self.company,
            name__in=['Rental Income', 'Investment Income', 'Dividend Income']
        )
        
        return JournalEntryLine.objects.filter(
            account__in=estate_accounts,
            journal_entry__date__range=[self.period.start, self.period.end]
        ).aggregate(total=Sum('credit'))['total'] or 0
