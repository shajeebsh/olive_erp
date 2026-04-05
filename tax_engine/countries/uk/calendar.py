"""
United Kingdom compliance deadlines
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
    recurring: str  # annual, monthly, quarterly

class UKComplianceCalendar:
    """Generate compliance deadlines for UK companies"""
    
    def __init__(self, company, year):
        self.company = company
        self.year = year
    
    def get_vat_deadlines(self) -> List[ComplianceDeadline]:
        """Get all VAT deadlines for the year"""
        from . import UKTaxEngine
        engine = UKTaxEngine()
        
        deadlines = []
        periods = engine.get_vat_periods(self.year)
        
        for period in periods:
            deadlines.append(ComplianceDeadline(
                name=f"VAT Return {period['name']}",
                description=f"File VAT return for period ending {period['end']}",
                due_date=date.fromisoformat(period['due']),
                form='VAT100',
                authority='HMRC',
                recurring='quarterly'
            ))
        
        return deadlines
    
    def get_ct_deadlines(self) -> List[ComplianceDeadline]:
        """Get Corporation Tax deadlines"""
        # CT600 due 12 months after accounting period end
        # Payment due 9 months and 1 day after
        from finance.models import FinancialPeriod
        
        fy_end = self.company.financial_year_end
        period_end = date(self.year, fy_end.month, fy_end.day)
        
        payment_due = period_end + timedelta(days=9*30 + 1)  # Simplified
        filing_due = period_end + timedelta(days=365)
        
        deadlines = [
            ComplianceDeadline(
                name="Corporation Tax Payment",
                description=f"Pay CT for year ended {period_end.strftime('%d/%m/%Y')}",
                due_date=payment_due,
                form='CT600 (payment)',
                authority='HMRC',
                recurring='annual'
            ),
            ComplianceDeadline(
                name="CT600 Return",
                description=f"File CT600 for year ended {period_end.strftime('%d/%m/%Y')}",
                due_date=filing_due,
                form='CT600',
                authority='HMRC',
                recurring='annual'
            )
        ]
        
        return deadlines
    
    def get_companies_house_deadlines(self) -> List[ComplianceDeadline]:
        """Get Companies House filing deadlines"""
        # Confirmation statement due within 14 days of made-up date
        # Accounts due 9 months after year end (private) or 6 months (public)
        
        from_date = date(self.year, 1, 1)
        made_up_date = from_date + timedelta(days=365)
        
        deadlines = [
            ComplianceDeadline(
                name="Confirmation Statement (CS01)",
                description=f"File confirmation statement made up to {made_up_date.strftime('%d/%m/%Y')}",
                due_date=made_up_date + timedelta(days=14),
                form='CS01',
                authority='Companies House',
                recurring='annual'
            ),
            ComplianceDeadline(
                name="Annual Accounts",
                description=f"File annual accounts for year ended {made_up_date.strftime('%d/%m/%Y')}",
                due_date=made_up_date + timedelta(days=9*30),  # 9 months
                form='AA',
                authority='Companies House',
                recurring='annual'
            )
        ]
        
        return deadlines
    
    def get_paye_deadlines(self) -> List[ComplianceDeadline]:
        """Get PAYE deadlines"""
        # Monthly FPS due on or before payment date
        # EPS due by 19th of following month
        # P60 due to employees by 31 May
        # P11D due to HMRC by 6 July
        
        deadlines = [
            ComplianceDeadline(
                name="P60 to Employees",
                description="Provide P60 to all employees",
                due_date=date(self.year + 1, 5, 31),
                form='P60',
                authority='HMRC',
                recurring='annual'
            ),
            ComplianceDeadline(
                name="P11D and P11D(b)",
                description="File expenses and benefits returns",
                due_date=date(self.year + 1, 7, 6),
                form='P11D',
                authority='HMRC',
                recurring='annual'
            ),
            ComplianceDeadline(
                name="PAYE Settlement Agreement",
                description="Submit PSA if applicable",
                due_date=date(self.year + 1, 7, 6),
                form='PSA',
                authority='HMRC',
                recurring='annual'
            )
        ]
        
        return deadlines
    
    def get_mtd_deadlines(self) -> List[ComplianceDeadline]:
        """Get Making Tax Digital deadlines"""
        # MTD quarterly updates due within 1 month of quarter end
        # Final declaration due 31 Jan following year end
        
        deadlines = [
            ComplianceDeadline(
                name="MTD Quarterly Update Q1",
                description="Submit MTD quarterly update (Apr-Jun)",
                due_date=date(self.year, 8, 7),
                form='MTD',
                authority='HMRC',
                recurring='quarterly'
            ),
            ComplianceDeadline(
                name="MTD Quarterly Update Q2",
                description="Submit MTD quarterly update (Jul-Sep)",
                due_date=date(self.year, 11, 7),
                form='MTD',
                authority='HMRC',
                recurring='quarterly'
            ),
            ComplianceDeadline(
                name="MTD Quarterly Update Q3",
                description="Submit MTD quarterly update (Oct-Dec)",
                due_date=date(self.year + 1, 2, 7),
                form='MTD',
                authority='HMRC',
                recurring='quarterly'
            ),
            ComplianceDeadline(
                name="MTD Final Declaration",
                description="Submit end of year declaration",
                due_date=date(self.year + 1, 1, 31),
                form='MTD',
                authority='HMRC',
                recurring='annual'
            )
        ]
        
        return deadlines
    
    def get_all_deadlines(self) -> List[ComplianceDeadline]:
        """Get all UK compliance deadlines for the year"""
        deadlines = []
        deadlines.extend(self.get_vat_deadlines())
        deadlines.extend(self.get_ct_deadlines())
        deadlines.extend(self.get_companies_house_deadlines())
        deadlines.extend(self.get_paye_deadlines())
        deadlines.extend(self.get_mtd_deadlines())
        
        # Sort by due date
        deadlines.sort(key=lambda x: x.due_date)
        
        return deadlines
