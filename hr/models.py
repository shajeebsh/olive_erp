from django.db import models
from django.conf import settings

class Department(models.Model):
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='departments', null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='employees', null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    job_title = models.CharField(max_length=100)
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=18, decimal_places=2)
    contact_info = models.TextField()
    address = models.TextField()
    emergency_contact = models.TextField()

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"

class LeaveRequest(models.Model):
    LEAVE_TYPES = (
        ('SICK', 'Sick'),
        ('VACATION', 'Vacation'),
        ('OTHER', 'Other'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='leave_requests', null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reason = models.TextField()

    def __str__(self):
        return f"{self.employee.user.username} - {self.leave_type}"

class Attendance(models.Model):
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='attendance_records', null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    check_in_time = models.TimeField()
    check_out_time = models.TimeField(null=True, blank=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.employee.user.username} - {self.date}"

class PayrollPeriod(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('PROCESSED', 'Processed'),
        ('PAID', 'Paid'),
    )
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='payroll_periods', null=True, blank=True)
    name = models.CharField(max_length=100)  # e.g. "April 2026"
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

class Payslip(models.Model):
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='payslips')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    basic_salary = models.DecimalField(max_digits=18, decimal_places=2)
    allowances = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=18, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.net_salary = self.basic_salary + self.allowances - self.deductions
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payslip {self.employee.employee_id} - {self.payroll_period.name}"
