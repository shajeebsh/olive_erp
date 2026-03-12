from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone
from django.db import transaction
from compliance.models import Filing, TaxPeriod
from compliance.countries.ie.models import (
    IrelandVATReturn, IrelandCTReturn, IrelandCROReturn,
    IrelandRBOFiling, IrelandPAYEReturn
)
from finance.models import JournalEntry, Account
from hr.models import Employee, PayrollRun
import logging

logger = logging.getLogger(__name__)


class IrelandTaxService:
    """
    Service for Ireland-specific tax computations and compliance.
    """
    
    # Ireland-specific tax rates and thresholds (2024)
    VAT_STANDARD_RATE = Decimal('23.00')  # 23%
    VAT_REDUCED_RATE = Decimal('13.50')   # 13.5%
    VAT_SECOND_REDUCED_RATE = Decimal('9.00')  # 9%
    
    CT_STANDARD_RATE = Decimal('12.50')   # 12.5%
    CT_CLOSE_COMPANY_RATE = Decimal('25.00')  # 25% for close companies
    
    PAYE_STANDARD_RATE = Decimal('20.00')  # 20% basic rate
    PAYE_HIGHER_RATE = Decimal('40.00')   # 40% higher rate
    
    PRSI_EMPLOYEE_RATE = Decimal('4.00')  # 4% employee PRSI
    PRSI_EMPLOYER_RATE = Decimal('11.05')  # 11.05% employer PRSI
    
    USC_RATES = {
        'standard': [
            (Decimal('12012'), Decimal('0.50')),  # 0.5% up to €12,012
            (Decimal('21720'), Decimal('2.00')),  # 2% up to €21,720
            (Decimal('70044'), Decimal('4.50')),  # 4.5% up to €70,044
            (Decimal('100000'), Decimal('8.00')),  # 8% up to €100,000
            (None, Decimal('11.00'))  # 11% over €100,000
        ]
    }
    
    @staticmethod
    def calculate_vat_return(company, period_start, period_end):
        """
        Calculate VAT return for a given period.
        """
        try:
            # Get sales and purchase journal entries for the period
            sales_entries = JournalEntry.objects.filter(
                company=company,
                date__range=[period_start, period_end],
                lines__account__type='INCOME'
            ).distinct()
            
            purchase_entries = JournalEntry.objects.filter(
                company=company,
                date__range=[period_start, period_end],
                lines__account__type='EXPENSE'
            ).distinct()
            
            # Calculate VAT amounts
            vat_on_sales = Decimal('0.00')
            vat_on_purchases = Decimal('0.00')
            
            # Simplified VAT calculation - in real implementation, this would
            # analyze each transaction and apply appropriate VAT rates
            for entry in sales_entries:
                vat_on_sales += entry.total_amount * IrelandTaxService.VAT_STANDARD_RATE / Decimal('100.00')
            
            for entry in purchase_entries:
                vat_on_purchases += entry.total_amount * IrelandTaxService.VAT_STANDARD_RATE / Decimal('100.00')
            
            net_vat_payable = vat_on_sales - vat_on_purchases
            
            return {
                'vat_on_sales': vat_on_sales,
                'vat_on_purchases': vat_on_purchases,
                'net_vat_payable': max(net_vat_payable, Decimal('0.00')),
                'vat_reclaimable': max(-net_vat_payable, Decimal('0.00'))
            }
            
        except Exception as e:
            logger.error(f"VAT calculation failed: {e}", exc_info=True)
            raise
    
    @staticmethod
    def calculate_corporation_tax(company, accounting_period_end):
        """
        Calculate corporation tax liability.
        """
        try:
            # Get profit/loss for the period
            profit_loss_account = Account.objects.get(
                company=company,
                code='3200'  # Assuming 3200 is P&L account
            )
            
            # Calculate taxable profit from journal entries
            period_start = accounting_period_end - timedelta(days=365)
            
            revenue_entries = JournalEntry.objects.filter(
                company=company,
                date__range=[period_start, accounting_period_end],
                lines__account__type='INCOME'
            )
            
            expense_entries = JournalEntry.objects.filter(
                company=company,
                date__range=[period_start, accounting_period_end],
                lines__account__type='EXPENSE'
            )
            
            total_revenue = sum(entry.total_amount for entry in revenue_entries)
            total_expenses = sum(entry.total_amount for entry in expense_entries)
            
            taxable_profit = total_revenue - total_expenses
            
            # Apply Ireland CT rate
            ct_liability = taxable_profit * IrelandTaxService.CT_STANDARD_RATE / Decimal('100.00')
            
            return {
                'taxable_profit': taxable_profit,
                'ct_rate': IrelandTaxService.CT_STANDARD_RATE,
                'ct_liability': ct_liability,
                'accounting_period': f"{period_start.strftime('%Y-%m-%d')} to {accounting_period_end.strftime('%Y-%m-%d')}"
            }
            
        except Exception as e:
            logger.error(f"Corporation tax calculation failed: {e}", exc_info=True)
            raise
    
    @staticmethod
    def calculate_paye_liability(company, period_start, period_end):
        """
        Calculate PAYE, PRSI, and USC liabilities for a period.
        """
        try:
            # Get payroll runs for the period
            payroll_runs = PayrollRun.objects.filter(
                company=company,
                pay_period_start=period_start,
                pay_period_end=period_end,
                is_processed=True
            )
            
            total_paye = Decimal('0.00')
            total_prsi_employee = Decimal('0.00')
            total_prsi_employer = Decimal('0.00')
            total_usc = Decimal('0.00')
            
            for payroll in payroll_runs:
                for detail in payroll.payroll_details.all():
                    # Calculate PAYE (simplified)
                    if detail.gross_pay > Decimal('40000'):
                        paye = (Decimal('40000') * IrelandTaxService.PAYE_STANDARD_RATE / Decimal('100.00') +
                               (detail.gross_pay - Decimal('40000')) * IrelandTaxService.PAYE_HIGHER_RATE / Decimal('100.00'))
                    else:
                        paye = detail.gross_pay * IrelandTaxService.PAYE_STANDARD_RATE / Decimal('100.00')
                    
                    # Calculate PRSI
                    prsi_employee = detail.gross_pay * IrelandTaxService.PRSI_EMPLOYEE_RATE / Decimal('100.00')
                    prsi_employer = detail.gross_pay * IrelandTaxService.PRSI_EMPLOYER_RATE / Decimal('100.00')
                    
                    # Calculate USC (simplified)
                    usc = Decimal('0.00')
                    remaining_income = detail.gross_pay
                    
                    for threshold, rate in IrelandTaxService.USC_RATES['standard']:
                        if threshold is None:
                            usc += remaining_income * rate / Decimal('100.00')
                            break
                        elif remaining_income > threshold:
                            usc += threshold * rate / Decimal('100.00')
                            remaining_income -= threshold
                        else:
                            usc += remaining_income * rate / Decimal('100.00')
                            break
                    
                    total_paye += paye
                    total_prsi_employee += prsi_employee
                    total_prsi_employer += prsi_employer
                    total_usc += usc
            
            return {
                'total_paye': total_paye,
                'total_prsi_employee': total_prsi_employee,
                'total_prsi_employer': total_prsi_employer,
                'total_usc': total_usc,
                'total_liability': total_paye + total_prsi_employee + total_prsi_employer + total_usc
            }
            
        except Exception as e:
            logger.error(f"PAYE calculation failed: {e}", exc_info=True)
            raise


class IrelandComplianceService:
    """
    Service for Ireland-specific compliance operations.
    """
    
    @staticmethod
    def create_vat_return_filing(company, period_start, period_end):
        """
        Create and populate a VAT return filing.
        """
        with transaction.atomic():
            # Create tax period
            tax_period, created = TaxPeriod.objects.get_or_create(
                company=company,
                start_date=period_start,
                end_date=period_end,
                defaults={
                    'period_type': TaxPeriod.PeriodType.QUARTERLY
                }
            )
            
            # Create filing
            filing = Filing.objects.create(
                company=company,
                tax_period=tax_period,
                filing_type=Filing.FilingType.VAT,
                due_date=period_end + timedelta(days=19)  # VAT returns due 19th of following month
            )
            
            # Calculate VAT
            vat_data = IrelandTaxService.calculate_vat_return(company, period_start, period_end)
            
            # Create VAT return
            vat_return = IrelandVATReturn.objects.create(
                filing=filing,
                vat_on_sales=vat_data['vat_on_sales'],
                vat_on_purchases=vat_data['vat_on_purchases'],
                net_vat_payable=vat_data['net_vat_payable'],
                total_vat_reclaimable=vat_data['vat_reclaimable'],
                vat_period=f"{period_start.strftime('%Y-%m')} to {period_end.strftime('%Y-%m')}",
                vat_number=company.vat_number or "Pending"
            )
            
            filing.amount_due = vat_data['net_vat_payable']
            filing.save()
            
            return filing
    
    @staticmethod
    def create_ct_return_filing(company, accounting_period_end):
        """
        Create and populate a Corporation Tax return filing.
        """
        with transaction.atomic():
            period_start = accounting_period_end - timedelta(days=365)
            
            tax_period, created = TaxPeriod.objects.get_or_create(
                company=company,
                start_date=period_start,
                end_date=accounting_period_end,
                defaults={
                    'period_type': TaxPeriod.PeriodType.ANNUAL
                }
            )
            
            # CT return due 21st of month following 9 months after accounting period end
            due_date = accounting_period_end + timedelta(days=9*30 + 21)
            
            filing = Filing.objects.create(
                company=company,
                tax_period=tax_period,
                filing_type=Filing.FilingType.CT,
                due_date=due_date
            )
            
            # Calculate CT
            ct_data = IrelandTaxService.calculate_corporation_tax(company, accounting_period_end)
            
            # Create CT return
            ct_return = IrelandCTReturn.objects.create(
                filing=filing,
                accounting_period=IrelandCTReturn.AccountingPeriod.STANDARD,
                trading_income=ct_data['taxable_profit'],
                taxable_profit=ct_data['taxable_profit'],
                ct_rate=ct_data['ct_rate'],
                ct_liability=ct_data['ct_liability'],
                ct_number=company.ct_number or "Pending",
                accounting_period_end=accounting_period_end
            )
            
            filing.amount_due = ct_data['ct_liability']
            filing.save()
            
            return filing
    
    @staticmethod
    def create_cro_return_filing(company, annual_return_date):
        """
        Create a CRO Annual Return filing.
        """
        with transaction.atomic():
            # CRO returns are due within 28 days of annual return date
            due_date = annual_return_date + timedelta(days=28)
            
            filing = Filing.objects.create(
                company=company,
                filing_type=Filing.FilingType.CRO,
                due_date=due_date
            )
            
            # Get company data for CRO return
            cro_return = IrelandCROReturn.objects.create(
                filing=filing,
                company_type=IrelandCROReturn.CompanyType.LTD,
                cro_number=company.cro_number or "Pending",
                registered_office=company.registered_address or "",
                authorized_share_capital=company.share_capital or Decimal('10000.00'),
                annual_return_date=annual_return_date
            )
            
            return filing
    
    @staticmethod
    def get_compliance_calendar(company):
        """
        Get upcoming compliance deadlines for a company.
        """
        today = timezone.now().date()
        deadlines = []
        
        # VAT deadlines (monthly/quarterly)
        vat_deadline = today.replace(day=19) + timedelta(days=32)
        vat_deadline = vat_deadline.replace(day=19)
        deadlines.append({
            'type': 'VAT',
            'description': 'VAT Return Filing',
            'due_date': vat_deadline,
            'days_remaining': (vat_deadline - today).days
        })
        
        # PAYE deadlines (monthly)
        paye_deadline = today.replace(day=14) + timedelta(days=32)
        paye_deadline = paye_deadline.replace(day=14)
        deadlines.append({
            'type': 'PAYE',
            'description': 'PAYE/PRSI Payment',
            'due_date': paye_deadline,
            'days_remaining': (paye_deadline - today).days
        })
        
        # CT deadlines (annual)
        if company.financial_year_end:
            ct_deadline = company.financial_year_end + timedelta(days=9*30 + 21)
            deadlines.append({
                'type': 'CT',
                'description': 'Corporation Tax Return',
                'due_date': ct_deadline,
                'days_remaining': (ct_deadline - today).days
            })
        
        # CRO deadlines (annual)
        if company.incorporation_date:
            cro_deadline = company.incorporation_date.replace(year=today.year)
            if cro_deadline < today:
                cro_deadline = cro_deadline.replace(year=today.year + 1)
            cro_deadline += timedelta(days=28)
            deadlines.append({
                'type': 'CRO',
                'description': 'CRO Annual Return',
                'due_date': cro_deadline,
                'days_remaining': (cro_deadline - today).days
            })
        
        return sorted(deadlines, key=lambda x: x['due_date'])