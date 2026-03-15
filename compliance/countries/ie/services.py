from django.template.loader import render_to_string
from django.utils import timezone
from datetime import date
from weasyprint import HTML
import tempfile

class CROB1Generator:
    """Generate CRO B1 Annual Return form"""
    
    def __init__(self, company, year):
        self.company = company
        self.year = year
        self.return_date = timezone.now().date()
    
    def get_annual_return_date(self):
        """Calculate ARD (Annual Return Date)"""
        # ARD is usually 6 months after financial year end
        fy_end = self.company.financial_year_end
        ard_month = fy_end.month + 6
        ard_year = fy_end.year
        
        if ard_month > 12:
            ard_month -= 12
            ard_year += 1
        
        return date(ard_year, ard_month, fy_end.day)
    
    def get_directors(self):
        """Get all directors as of return date"""
        from .models import Director
        return Director.objects.filter(
            company=self.company,
            appointment_date__lte=self.return_date
        ).exclude(
            resignation_date__lte=self.return_date
        ).order_by('appointment_date')
    
    def get_secretary(self):
        """Get current secretary"""
        from .models import Secretary
        return Secretary.objects.filter(
            company=self.company,
            appointment_date__lte=self.return_date
        ).exclude(
            resignation_date__lte=self.return_date
        ).first()
    
    def get_shareholders(self):
        """Get all shareholders"""
        from .models import Shareholder
        return Shareholder.objects.filter(
            company=self.company
        ).order_by('-percentage_held')
    
    def get_share_capital(self):
        """Get share capital structure"""
        from .models import OrdinaryShare, PreferenceShare
        return {
            'ordinary': OrdinaryShare.objects.filter(company=self.company).first(),
            'preference': PreferenceShare.objects.filter(company=self.company).first()
        }
    
    def generate_pdf(self):
        """Generate B1 form as PDF"""
        context = {
            'company': self.company,
            'year': self.year,
            'return_date': self.return_date,
            'ard': self.get_annual_return_date(),
            'directors': self.get_directors(),
            'secretary': self.get_secretary(),
            'shareholders': self.get_shareholders(),
            'share_capital': self.get_share_capital(),
            'financial_statements': self.get_financial_statements(),
        }
        
        html_string = render_to_string('compliance/ie/cro_b1.html', context)
        
        # Generate PDF
        pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        HTML(string=html_string).write_pdf(pdf_file.name)
        
        return pdf_file.name
    
    def get_financial_statements(self):
        """Get P&L and Balance Sheet for the year"""
        from finance.reports import FinancialReports
        
        fy_end = self.company.financial_year_end
        fy_start = date(fy_end.year - 1, fy_end.month, fy_end.day)
        
        return {
            'profit_loss': FinancialReports.profit_loss(
                fy_start, fy_end, self.company.id
            ),
            'balance_sheet': FinancialReports.balance_sheet(
                fy_end, self.company.id
            )
        }