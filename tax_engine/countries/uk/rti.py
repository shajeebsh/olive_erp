from decimal import Decimal
from datetime import date, datetime
from django.db.models import Sum
from typing import Dict, List

class RTICalculator:
    """
    Real Time Information - PAYE calculations
    
    Tax rates (2025):
    - Personal Allowance: £12,570 (0%)
    - Basic Rate: £12,571 to £50,270 (20%)
    - Higher Rate: £50,271 to £125,140 (40%)
    - Additional Rate: over £125,140 (45%)
    
    National Insurance (2025):
    - Primary Class 1: 8% between £12,570 and £50,270
    - Secondary Class 1: 13.8% above £9,100
    """
    
    # Tax bands
    PERSONAL_ALLOWANCE = Decimal('12570')
    BASIC_RATE_LIMIT = Decimal('50270')
    HIGHER_RATE_LIMIT = Decimal('125140')
    
    # Tax rates
    BASIC_RATE = Decimal('0.20')
    HIGHER_RATE = Decimal('0.40')
    ADDITIONAL_RATE = Decimal('0.45')
    
    # NI thresholds and rates
    PRIMARY_THRESHOLD = Decimal('12570')  # Lower Earnings Limit
    UPPER_EARNINGS_LIMIT = Decimal('50270')
    SECONDARY_THRESHOLD = Decimal('9100')  # Employer NI starts
    
    PRIMARY_RATE = Decimal('0.08')  # 8% between PT and UEL
    SECONDARY_RATE = Decimal('0.138')  # 13.8% above ST
    
    def __init__(self, employee, tax_year):
        self.employee = employee
        self.tax_year = tax_year  # e.g., '2025-26'
    
    def get_tax_code(self):
        """Get employee's tax code (e.g., '1257L')"""
        # Default to standard code
        return getattr(self.employee, 'tax_code', '1257L')
    
    def get_ni_category(self):
        """Get NI category letter (A, B, C, etc.)"""
        # Default to category A (standard)
        return getattr(self.employee, 'ni_category', 'A')
    
    def calculate_tax(self, pay_period: Decimal, cumulative_pay: Decimal) -> Decimal:
        """
        Calculate PAYE tax using cumulative basis
        
        Args:
            pay_period: Pay for this period
            cumulative_pay: Total pay year to date
        """
        total_pay = cumulative_pay + pay_period
        
        # Calculate tax on total pay
        tax = Decimal('0.00')
        remaining = total_pay
        
        # Personal allowance
        if remaining > self.PERSONAL_ALLOWANCE:
            remaining -= self.PERSONAL_ALLOWANCE
            
            # Basic rate
            basic_band = min(remaining, self.BASIC_RATE_LIMIT - self.PERSONAL_ALLOWANCE)
            tax += basic_band * self.BASIC_RATE
            remaining -= basic_band
            
            # Higher rate
            if remaining > 0:
                higher_band = min(remaining, self.HIGHER_RATE_LIMIT - self.BASIC_RATE_LIMIT)
                tax += higher_band * self.HIGHER_RATE
                remaining -= higher_band
                
                # Additional rate
                if remaining > 0:
                    tax += remaining * self.ADDITIONAL_RATE
        else:
            # Under personal allowance, no tax
            tax = Decimal('0.00')
        
        # Apply Scottish rates if applicable (simplified)
        if getattr(self.employee, 'country', 'UK') == 'Scotland':
            # Scottish rates differ - would need separate implementation
            pass
        
        return tax
    
    def calculate_ni(self, pay_period: Decimal, cumulative_pay: Decimal) -> Dict:
        """
        Calculate National Insurance contributions
        
        Returns:
            {'employee': employee_ni, 'employer': employer_ni}
        """
        total_pay = cumulative_pay + pay_period
        
        # Calculate employee NI (Class 1 primary)
        employee_ni = Decimal('0.00')
        
        if total_pay > self.PRIMARY_THRESHOLD:
            # Calculate on this period's earnings between PT and UEL
            pay_this_period = pay_period
            
            # Adjust for cumulative thresholds
            if cumulative_pay < self.PRIMARY_THRESHOLD:
                # Some of this period falls below threshold
                threshold_remaining = self.PRIMARY_THRESHOLD - cumulative_pay
                if pay_this_period > threshold_remaining:
                    chargeable = pay_this_period - threshold_remaining
                    # Cap at UEL
                    uel_remaining = max(Decimal('0.00'), self.UPPER_EARNINGS_LIMIT - max(cumulative_pay, self.PRIMARY_THRESHOLD))
                    chargeable = min(chargeable, uel_remaining)
                    employee_ni = chargeable * self.PRIMARY_RATE
            else:
                # Already above PT
                uel_remaining = max(Decimal('0.00'), self.UPPER_EARNINGS_LIMIT - cumulative_pay)
                chargeable = min(pay_this_period, uel_remaining)
                employee_ni = chargeable * self.PRIMARY_RATE
        
        # Calculate employer NI (Class 1 secondary)
        employer_ni = Decimal('0.00')
        
        # Employer NI on pay above Secondary Threshold
        if total_pay > self.SECONDARY_THRESHOLD:
            if cumulative_pay < self.SECONDARY_THRESHOLD:
                threshold_remaining = self.SECONDARY_THRESHOLD - cumulative_pay
                if pay_period > threshold_remaining:
                    chargeable = pay_period - threshold_remaining
                    employer_ni = chargeable * self.SECONDARY_RATE
            else:
                # All of this period above threshold
                employer_ni = pay_period * self.SECONDARY_RATE
        
        return {
            'employee': employee_ni.quantize(Decimal('0.01')),
            'employer': employer_ni.quantize(Decimal('0.01'))
        }
    
    def calculate_payslip(self, gross_pay: Decimal, period_number: int) -> Dict:
        """
        Complete payslip calculation
        
        Args:
            gross_pay: Gross pay for period
            period_number: 1-12 for monthly, 1-52 for weekly
        """
        from hr.models import Payslip
        
        # Get cumulative pay this year
        cumulative_payslips = Payslip.objects.filter(
            employee=self.employee,
            pay_date__year=date.today().year,
            period_number__lt=period_number
        )
        
        cumulative_gross = cumulative_payslips.aggregate(total=Sum('gross_pay'))['total'] or 0
        
        # Calculate deductions
        tax = self.calculate_tax(gross_pay, cumulative_gross)
        ni = self.calculate_ni(gross_pay, cumulative_gross)
        
        # Student loan (if applicable)
        student_loan = self.calculate_student_loan(gross_pay, cumulative_gross)
        
        # Pension (if applicable)
        pension = self.calculate_pension(gross_pay)
        
        total_deductions = tax + ni['employee'] + student_loan + pension['employee']
        net_pay = gross_pay - total_deductions
        
        return {
            'gross_pay': float(gross_pay),
            'deductions': {
                'paye_tax': float(tax),
                'employee_ni': float(ni['employee']),
                'employer_ni': float(ni['employer']),
                'student_loan': float(student_loan),
                'pension_employee': float(pension['employee']),
                'pension_employer': float(pension['employer']),
                'total_deductions': float(total_deductions)
            },
            'net_pay': float(net_pay),
            'employer_costs': float(gross_pay + ni['employer'] + pension['employer']),
            'tax_code': self.get_tax_code(),
            'ni_category': self.get_ni_category()
        }
    
    def calculate_student_loan(self, gross_pay: Decimal, cumulative_gross: Decimal) -> Decimal:
        """Calculate student loan deduction (Plan 1, 2, 4)"""
        # Plan thresholds vary - simplified example
        if not getattr(self.employee, 'has_student_loan', False):
            return Decimal('0.00')
        
        # Plan 1: 9% above £22,015 (weekly £424)
        threshold = Decimal('22015')
        plan_type = getattr(self.employee, 'student_loan_plan', '1')
        
        if plan_type == '1':
            annual_threshold = Decimal('22015')
        elif plan_type == '2':
            annual_threshold = Decimal('27295')
        else:
            return Decimal('0.00')
        
        # Check if above threshold
        total_gross = cumulative_gross + gross_pay
        if total_gross > annual_threshold:
            # Calculate on this period
            # Simplified - actual uses cumulative
            return gross_pay * Decimal('0.09')
        
        return Decimal('0.00')
    
    def calculate_pension(self, gross_pay: Decimal) -> Dict:
        """Calculate pension contributions"""
        if not getattr(self.employee, 'has_pension', False):
            return {'employee': Decimal('0.00'), 'employer': Decimal('0.00')}
        
        # Auto-enrolment minimums
        employee_rate = Decimal('0.05')  # 5% employee
        employer_rate = Decimal('0.03')  # 3% employer (simplified)
        
        # Qualifying earnings band (simplified)
        qualifying_earnings = gross_pay  # In reality, only pay between thresholds
        
        return {
            'employee': qualifying_earnings * employee_rate,
            'employer': qualifying_earnings * employer_rate
        }

class RTISubmission:
    """
    RTI submission to HMRC (FPS - Full Payment Submission)
    """
    
    def __init__(self, company):
        self.company = company
        self.employer_ref = getattr(company, 'paye_reference', '123/AB45678')  # e.g., '123/AB45678'
    
    def generate_fps_xml(self, payslips: List, period: Dict) -> str:
        """
        Generate FPS XML for HMRC
        In production, would generate full HMRC schema
        """
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom import minidom
        
        root = Element('IRenvelope')
        root.set('xmlns', 'http://www.govtalk.gov.uk/taxation/PAYE/RTI/16-17/1')
        
        # Header
        header = SubElement(root, 'Header')
        SubElement(header, 'MessageType').text = 'FPS'
        SubElement(header, 'MessageId').text = f"FPS{date.today().strftime('%Y%m%d%H%M%S')}"
        SubElement(header, 'TimeStamp').text = datetime.now().isoformat()
        
        # Employer details
        employer = SubElement(root, 'Employer')
        SubElement(employer, 'PAYEReference').text = self.employer_ref
        
        # Payment period
        payment = SubElement(root, 'Payment')
        SubElement(payment, 'TaxYear').text = str(period['tax_year'])
        SubElement(payment, 'PayFrequency').text = period['frequency']
        SubElement(payment, 'PeriodCovered').text = str(period['number'])
        SubElement(payment, 'DateOfPayment').text = date.today().isoformat()
        
        # Employee details
        employees = SubElement(root, 'Employees')
        for payslip in payslips:
            emp = SubElement(employees, 'Employee')
            SubElement(emp, 'NINO').text = getattr(payslip.employee, 'ni_number', '')
            SubElement(emp, 'Surname').text = payslip.employee.last_name
            SubElement(emp, 'Forename').text = payslip.employee.first_name
            SubElement(emp, 'DateOfBirth').text = getattr(payslip.employee, 'date_of_birth', date(1980, 1, 1)).isoformat()
            
            # Pay and deductions
            pay = SubElement(emp, 'PayAndDeductions')
            SubElement(pay, 'GrossPay').text = str(payslip.gross_pay)
            SubElement(pay, 'PAYEDeducted').text = str(getattr(payslip, 'paye_deducted', 0))
            SubElement(pay, 'NIDeducted').text = str(getattr(payslip, 'ni_deducted', 0))
            SubElement(pay, 'StudentLoanDeducted').text = str(getattr(payslip, 'student_loan_deducted', 0))
        
        # Pretty print XML
        xml_str = minidom.parseString(tostring(root)).toprettyxml(indent="  ")
        return xml_str
    
    def submit_to_hmrc(self, fps_xml: str) -> Dict:
        """
        Submit FPS to HMRC
        In production, would use HMRC API with proper authentication
        """
        # Mock response
        return {
            'status': 'accepted',
            'correlation_id': f'CORR{date.today().strftime("%Y%m%d%H%M%S")}',
            'acknowledgment': 'Your submission has been accepted',
            'received_at': datetime.now().isoformat()
        }
    
    def generate_p60(self, employee, tax_year) -> bytes:
        """Generate P60 PDF for employee"""
        from django.template.loader import render_to_string
        from weasyprint import HTML
        
        context = {
            'employee': employee,
            'company': self.company,
            'tax_year': tax_year,
            'total_pay': employee.total_pay_for_year(tax_year) if hasattr(employee, 'total_pay_for_year') else 0,
            'total_tax': employee.total_tax_for_year(tax_year) if hasattr(employee, 'total_tax_for_year') else 0,
            'ni_number': getattr(employee, 'ni_number', ''),
            'tax_code': getattr(employee, 'tax_code', '1257L')
        }
        
        html_string = render_to_string('tax_engine/uk/p60.html', context)
        
        # Generate PDF
        import tempfile
        pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        HTML(string=html_string).write_pdf(pdf_file.name)
        
        with open(pdf_file.name, 'rb') as f:
            return f.read()
