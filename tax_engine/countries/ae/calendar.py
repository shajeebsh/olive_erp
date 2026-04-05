"""
UAE compliance deadlines
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
    recurring: str
    penalty: str = ""

class UAEComplianceCalendar:
    """Generate compliance deadlines for UAE companies"""
    
    def __init__(self, company, year):
        self.company = company
        self.year = year
    
    def get_vat_deadlines(self) -> List[ComplianceDeadline]:
        """Get all VAT deadlines for the year"""
        from . import UAETaxEngine
        engine = UAETaxEngine()
        
        deadlines = []
        periods = engine.get_vat_periods(self.year)
        
        for period in periods:
            deadlines.append(ComplianceDeadline(
                name=f"VAT Return {period['name']}",
                description=f"File VAT 201 for {period['name']}",
                due_date=date.fromisoformat(period['due']),
                form='VAT201',
                authority='FTA',
                recurring='quarterly',
                penalty="Late filing: AED 1,000-2,000. Late payment: 2% immediate, 4% after 7 days, 1% daily after 30 days (max 300%)"
            ))
        
        return deadlines
    
    def get_excise_deadlines(self) -> List[ComplianceDeadline]:
        """Get Excise Tax deadlines (monthly)"""
        deadlines = []
        
        for month in range(1, 13):
            period_end = date(self.year, month, 1).replace(day=1) + timedelta(days=32)
            period_end = period_end.replace(day=1) - timedelta(days=1)
            
            if month == 12:
                due_date = date(self.year + 1, 1, 28)
            else:
                due_date = date(self.year, month + 1, 28)
            
            deadlines.append(ComplianceDeadline(
                name=f"Excise Tax Declaration {period_end.strftime('%B %Y')}",
                description=f"File monthly excise declaration for {period_end.strftime('%B %Y')}",
                due_date=due_date,
                form='Excise Declaration',
                authority='FTA',
                recurring='monthly',
                penalty="Late filing penalties apply"
            ))
        
        return deadlines
    
    def get_corporate_tax_deadlines(self) -> List[ComplianceDeadline]:
        """Get Corporate Tax deadlines"""
        # CT returns due within 9 months of financial year end
        fy_start = self.company.fiscal_year_start_date
        if not fy_start:
             fy_end_date = date(self.year, 12, 31)
        else:
             fy_end_date = fy_start.replace(year=self.year) - timedelta(days=1)
             if fy_end_date.year < self.year:
                 fy_end_date = fy_end_date.replace(year=self.year)
        
        ct_due = fy_end_date + timedelta(days=9*30)  # 9 months approx
        
        deadlines = [
            ComplianceDeadline(
                name="Corporate Tax Return",
                description=f"File Corporate Tax return for year ended {fy_end_date.strftime('%d/%m/%Y')}",
                due_date=ct_due,
                form='CT Return',
                authority='FTA',
                recurring='annual',
                penalty="Late filing: AED 1,000-2,000. Late payment: 2% immediate, 4% after 7 days, 1% daily after 30 days"
            )
        ]
        
        return deadlines
    
    def get_economic_substance_deadlines(self) -> List[ComplianceDeadline]:
        """Get Economic Substance Regulation (ESR) deadlines"""
        # ESR notifications due within 12 months of year end
        fy_start = self.company.fiscal_year_start_date
        if not fy_start:
             fy_end_date = date(self.year, 12, 31)
        else:
             fy_end_date = fy_start.replace(year=self.year) - timedelta(days=1)
             if fy_end_date.year < self.year:
                 fy_end_date = fy_end_date.replace(year=self.year)
        esr_due = fy_end_date + timedelta(days=365)
        
        deadlines = [
            ComplianceDeadline(
                name="ESR Notification",
                description="File Economic Substance Regulation notification",
                due_date=esr_due,
                form='ESR Notification',
                authority='MOE',
                recurring='annual',
                penalty="AED 20,000 - 50,000"
            ),
            ComplianceDeadline(
                name="ESR Report",
                description="File Economic Substance Regulation report (if applicable)",
                due_date=esr_due + timedelta(days=30),
                form='ESR Report',
                authority='MOE',
                recurring='annual',
                penalty="AED 50,000 - 400,000"
            )
        ]
        
        return deadlines
    
    def get_ultimate_beneficial_owner_deadlines(self) -> List[ComplianceDeadline]:
        """Get UBO register deadlines"""
        deadlines = [
            ComplianceDeadline(
                name="UBO Register Maintenance",
                description="Maintain Ultimate Beneficial Owner register",
                due_date=date(self.year, 12, 31),
                form='UBO Register',
                authority='MOE',
                recurring='annual',
                penalty="AED 10,000 - 100,000"
            )
        ]
        
        return deadlines
    
    def get_all_deadlines(self) -> List[ComplianceDeadline]:
        """Get all UAE compliance deadlines for the year"""
        deadlines = []
        deadlines.extend(self.get_vat_deadlines())
        deadlines.extend(self.get_excise_deadlines())
        deadlines.extend(self.get_corporate_tax_deadlines())
        deadlines.extend(self.get_economic_substance_deadlines())
        deadlines.extend(self.get_ultimate_beneficial_owner_deadlines())
        
        # Sort by due date
        deadlines.sort(key=lambda x: x.due_date)
        
        return deadlines
