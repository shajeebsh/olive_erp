"""
PAYE Modernisation - Real-time reporting to Revenue
"""
from decimal import Decimal
from datetime import date
from django.db.models import Sum

class PAYECalculator:
    """Calculate PAYE, PRSI, USC for employees"""
    
    # 2025 rates (simplified - update with actual rates)
    PAYE_RATES = [
        {'rate': Decimal('0.20'), 'threshold': Decimal('42000')},  # 20% up to 42,000
        {'rate': Decimal('0.40'), 'threshold': None},  # 40% above
    ]
    
    PRSI_RATES = {
        'class_a': Decimal('0.04'),  # 4% employee PRSI
        'employer': Decimal('0.087'),  # 8.7% employer PRSI
    }
    
    USC_RATES = [
        {'rate': Decimal('0.005'), 'threshold': Decimal('12012')},   # 0.5% up to 12,012
        {'rate': Decimal('0.02'), 'threshold': Decimal('25760')},    # 2% up to 25,760
        {'rate': Decimal('0.045'), 'threshold': Decimal('70044')},   # 4.5% up to 70,044
        {'rate': Decimal('0.08'), 'threshold': None},                # 8% above
    ]
    
    def __init__(self, employee, pay_date):
        self.employee = employee
        self.pay_date = pay_date
        
    def get_cumulative_pay(self, tax_year):
        """Get cumulative pay for tax year to date"""
        from hr.models import Payslip
        
        payslips = Payslip.objects.filter(
            employee=self.employee,
            pay_date__year=tax_year,
            pay_date__lte=self.pay_date
        )
        
        return payslips.aggregate(total=Sum('gross_pay'))['total'] or 0
    
    def calculate_paye(self, gross_pay, tax_credits=Decimal('3750')):
        """Calculate PAYE using cumulative basis"""
        cumulative_pay = self.get_cumulative_pay(self.pay_date.year)
        total_pay = cumulative_pay + gross_pay
        
        # Calculate total tax due for year to date
        total_tax = Decimal('0.00')
        remaining = total_pay
        for bracket in self.PAYE_RATES:
            if remaining <= 0:
                break
            if bracket['threshold']:
                taxable = min(remaining, bracket['threshold'])
                total_tax += taxable * bracket['rate']
                remaining -= taxable
            else:
                total_tax += remaining * bracket['rate']
                remaining = 0
        
        # Apply tax credits
        total_tax = max(Decimal('0.00'), total_tax - tax_credits)
        
        # Calculate tax already paid this year
        from hr.models import Payslip
        tax_paid = Payslip.objects.filter(
            employee=self.employee,
            pay_date__year=self.pay_date.year,
            pay_date__lte=self.pay_date
        ).aggregate(total=Sum('paye_deducted'))['total'] or 0
        
        # Tax due on this payslip
        paye_due = total_tax - tax_paid
        
        return max(Decimal('0.00'), paye_due)
    
    def calculate_prsi(self, gross_pay):
        """Calculate PRSI (employee contribution)"""
        return gross_pay * self.PRSI_RATES['class_a']
    
    def calculate_employer_prsi(self, gross_pay):
        """Calculate employer PRSI contribution"""
        return gross_pay * self.PRSI_RATES['employer']
    
    def calculate_usc(self, gross_pay):
        """Calculate Universal Social Charge"""
        cumulative_pay = self.get_cumulative_pay(self.pay_date.year)
        total_pay = cumulative_pay + gross_pay
        
        # Calculate total USC for year to date
        total_usc = Decimal('0.00')
        remaining = total_pay
        for bracket in self.USC_RATES:
            if remaining <= 0:
                break
            if bracket['threshold']:
                taxable = min(remaining, bracket['threshold'])
                total_usc += taxable * bracket['rate']
                remaining -= taxable
            else:
                total_usc += remaining * bracket['rate']
                remaining = 0
        
        # USC already paid
        from hr.models import Payslip
        usc_paid = Payslip.objects.filter(
            employee=self.employee,
            pay_date__year=self.pay_date.year,
            pay_date__lte=self.pay_date
        ).aggregate(total=Sum('usc_deducted'))['total'] or 0
        
        return max(Decimal('0.00'), total_usc - usc_paid)
    
    def calculate_payslip(self, gross_pay):
        """Complete payslip calculation"""
        paye = self.calculate_paye(gross_pay)
        prsi = self.calculate_prsi(gross_pay)
        usc = self.calculate_usc(gross_pay)
        employer_prsi = self.calculate_employer_prsi(gross_pay)
        
        total_deductions = paye + prsi + usc
        net_pay = gross_pay - total_deductions
        
        return {
            'gross_pay': gross_pay,
            'paye': paye,
            'prsi': prsi,
            'usc': usc,
            'total_deductions': total_deductions,
            'net_pay': net_pay,
            'employer_prsi': employer_prsi,
            'employer_costs': gross_pay + employer_prsi
        }

class RevenueSubmission:
    """Handle real-time PAYE submissions to Revenue"""
    
    def __init__(self, company):
        self.company = company
        self.revenue_id = company.revenue_id  # ROS credentials
    
    def generate_payslip_xml(self, payslip):
        """Generate Revenue-compatible XML for single payslip"""
        from xml.etree.ElementTree import Element, SubElement, tostring
        
        root = Element('PayrollSubmission')
        root.set('xmlns', 'http://www.revenue.ie/schema/paye-mod')
        
        # Employer details
        employer = SubElement(root, 'Employer')
        SubElement(employer, 'RevenueID').text = self.revenue_id
        SubElement(employer, 'CompanyName').text = self.company.name
        
        # Employee details
        employee = SubElement(root, 'Employee')
        SubElement(employee, 'PPSN').text = payslip.employee.ppsn
        SubElement(employee, 'FirstName').text = payslip.employee.first_name
        SubElement(employee, 'LastName').text = payslip.employee.last_name
        
        # Payment details
        payment = SubElement(root, 'Payment')
        SubElement(payment, 'PaymentDate').text = payslip.pay_date.isoformat()
        SubElement(payment, 'GrossPay').text = str(payslip.gross_pay)
        SubElement(payment, 'PAYE').text = str(payslip.paye_deducted)
        SubElement(payment, 'PRSI').text = str(payslip.prsi_deducted)
        SubElement(payment, 'USC').text = str(payslip.usc_deducted)
        SubElement(payment, 'NetPay').text = str(payslip.net_pay)
        
        return tostring(root, encoding='unicode')
    
    def submit_to_revenue(self, payslip_xml):
        """Submit to Revenue (stub - would use ROS API)"""
        # In production, this would call Revenue's API
        # For now, return mock response
        return {
            'status': 'accepted',
            'acknowledgment_id': f'REV{date.today().strftime("%Y%m%d%H%M%S")}',
            'received_at': date.today().isoformat()
        }
