"""
Ireland compliance deadlines calendar
"""
from datetime import date, timedelta
from dataclasses import dataclass
from typing import List

@dataclass
class ComplianceDeadline:
    name: str
    description: str
    due_date: date
    form: str
    authority: str
    recurring: str  # annual, monthly, quarterly, bi-monthly

class IrelandComplianceCalendar:
    """Generate compliance deadlines for Irish companies"""
    
    def __init__(self, company, year):
        self.company = company
        self.year = year
    
    def get_vat_deadlines(self) -> List[ComplianceDeadline]:
        """Get all VAT deadlines for the year"""
        from . import IrelandTaxEngine
        engine = IrelandTaxEngine()
        
        deadlines = []
        periods = engine.get_tax_periods(self.year)
        
        for period in periods:
            deadlines.append(ComplianceDeadline(
                name=f"VAT Return {period['name']}",
                description=f"File VAT3 for period ending {period['end']}",
                due_date=date.fromisoformat(period['due']),
                form='VAT3',
                authority='Revenue',
                recurring='bi-monthly'
            ))
        
        return deadlines
    
    def get_cro_deadlines(self) -> List[ComplianceDeadline]:
        """Get CRO filing deadlines"""
        # Annual Return Date (ARD) - 6 months after financial year end
        fy_end = self.company.financial_year_end
        ard = date(self.year, fy_end.month, fy_end.day) + timedelta(days=180)
        
        # B1 due within 56 days of ARD
        b1_due = ard + timedelta(days=56)
        
        deadlines = [
            ComplianceDeadline(
                name="Annual Return (B1)",
                description=f"File B1 within 56 days of ARD ({ard.strftime('%d/%m/%Y')})",
                due_date=b1_due,
                form='B1',
                authority='CRO',
                recurring='annual'
            )
        ]
        
        return deadlines
    
    def get_ct_deadlines(self) -> List[ComplianceDeadline]:
        """Get Corporation Tax deadlines"""
        # Preliminary tax: 31 Oct in year of accounting period
        preliminary_tax_due = date(self.year, 10, 31)
        
        # CT1 due: 9 months after year end
        fy_end = self.company.financial_year_end
        ct1_due = date(self.year, fy_end.month, fy_end.day) + timedelta(days=270)
        
        deadlines = [
            ComplianceDeadline(
                name="Preliminary Corporation Tax",
                description="Pay preliminary tax for current year",
                due_date=preliminary_tax_due,
                form='CT1 (payment)',
                authority='Revenue',
                recurring='annual'
            ),
            ComplianceDeadline(
                name="CT1 Return",
                description=f"File CT1 for year ended {fy_end.strftime('%d/%m/%Y')}",
                due_date=ct1_due,
                form='CT1',
                authority='Revenue',
                recurring='annual'
            )
        ]
        
        return deadlines
    
    def get_rbo_deadlines(self) -> List[ComplianceDeadline]:
        """Get RBO filing deadlines"""
        # RBO must be updated within 14 days of any change
        # Annual confirmation due within 28 days of ARD
        fy_end = self.company.financial_year_end
        ard = date(self.year, fy_end.month, fy_end.day) + timedelta(days=180)
        rbo_confirm_due = ard + timedelta(days=28)
        
        deadlines = [
            ComplianceDeadline(
                name="RBO Annual Confirmation",
                description="Confirm beneficial ownership details",
                due_date=rbo_confirm_due,
                form='RBO',
                authority='RBO',
                recurring='annual'
            )
        ]
        
        return deadlines
    
    def get_paye_deadlines(self) -> List[ComplianceDeadline]:
        """Get PAYE deadlines"""
        # Monthly PAYE due by 14th of following month
        deadlines = []
        for month in range(1, 13):
            pay_date = date(self.year, month, 1)
            due_date = date(self.year, month + 1, 14) if month < 12 else date(self.year + 1, 1, 14)
            
            deadlines.append(ComplianceDeadline(
                name=f"PAYE/PRSI {pay_date.strftime('%B %Y')}",
                description=f"Pay and file PAYE/PRSI/USC for {pay_date.strftime('%B %Y')}",
                due_date=due_date,
                form='PAYE',
                authority='Revenue',
                recurring='monthly'
            ))
        
        # P35 annual return due 14 Feb
        deadlines.append(ComplianceDeadline(
            name="P35 Annual Return",
            description="File annual P35 employer return",
            due_date=date(self.year + 1, 2, 14),
            form='P35',
            authority='Revenue',
            recurring='annual'
        ))
        
        return deadlines
    
    def get_all_deadlines(self) -> List[ComplianceDeadline]:
        """Get all compliance deadlines for the year"""
        deadlines = []
        deadlines.extend(self.get_vat_deadlines())
        deadlines.extend(self.get_cro_deadlines())
        deadlines.extend(self.get_ct_deadlines())
        deadlines.extend(self.get_rbo_deadlines())
        deadlines.extend(self.get_paye_deadlines())
        
        # Sort by due date
        deadlines.sort(key=lambda x: x.due_date)
        
        return deadlines
