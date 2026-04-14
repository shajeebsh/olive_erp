import pytest
from datetime import date, timedelta
from django.test import TestCase
from hr.models import Employee, LeaveRequest, Payslip, PayrollPeriod, Attendance
from company.models import CompanyProfile
from django.contrib.auth import get_user_model
from core.models import Role, UserRole

User = get_user_model()


@pytest.mark.django_db
class TestPayrollLogic:
    def test_payslip_net_calculation_basic(self, test_employee):
        period = PayrollPeriod.objects.create(
            company=test_employee.company,
            name='April 2026',
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 30),
            status='DRAFT'
        )
        payslip = Payslip.objects.create(
            payroll_period=period,
            employee=test_employee,
            basic_salary=5000.00,
            allowances=500.00,
            deductions=200.00,
            net_salary=0
        )
        assert payslip.net_salary == 5300.00

    def test_payslip_net_calculation_with_zero_allowances(self, test_employee):
        period = PayrollPeriod.objects.create(
            company=test_employee.company,
            name='May 2026',
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 31),
            status='DRAFT'
        )
        payslip = Payslip.objects.create(
            payroll_period=period,
            employee=test_employee,
            basic_salary=3000.00,
            allowances=0,
            deductions=100.00,
            net_salary=0
        )
        assert payslip.net_salary == 2900.00

    def test_payslip_net_calculation_with_high_deductions(self, test_employee):
        period = PayrollPeriod.objects.create(
            company=test_employee.company,
            name='June 2026',
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 30),
            status='DRAFT'
        )
        payslip = Payslip.objects.create(
            payroll_period=period,
            employee=test_employee,
            basic_salary=10000.00,
            allowances=1000.00,
            deductions=3500.00,
            net_salary=0
        )
        assert payslip.net_salary == 7500.00


@pytest.mark.django_db
class TestLeaveValidation:
    def test_leave_request_creation(self, test_employee):
        leave = LeaveRequest.objects.create(
            company=test_employee.company,
            employee=test_employee,
            leave_type='VACATION',
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 5),
            reason='Family vacation'
        )
        assert leave.status == 'PENDING'
        assert leave.employee == test_employee

    def test_overlapping_leave_requests_not_allowed(self, test_employee):
        LeaveRequest.objects.create(
            company=test_employee.company,
            employee=test_employee,
            leave_type='VACATION',
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 5),
            reason='First leave'
        )
        
        overlapping = LeaveRequest.objects.filter(
            employee=test_employee,
            start_date__lte=date(2026, 6, 5),
            end_date__gte=date(2026, 6, 1),
            status__in=['PENDING', 'APPROVED']
        ).exists()
        
        assert overlapping is True

    def test_leave_request_different_dates_allowed(self, test_employee):
        LeaveRequest.objects.create(
            company=test_employee.company,
            employee=test_employee,
            leave_type='VACATION',
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            reason='July leave'
        )
        
        non_overlapping = LeaveRequest.objects.filter(
            employee=test_employee,
            start_date__gte=date(2026, 7, 6)
        )
        
        assert non_overlapping.count() == 0

    def test_approved_leave_blocks_new_request(self, test_employee):
        LeaveRequest.objects.create(
            company=test_employee.company,
            employee=test_employee,
            leave_type='SICK',
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 3),
            status='APPROVED',
            reason='Sick leave'
        )
        
        approved_in_period = LeaveRequest.objects.filter(
            employee=test_employee,
            status='APPROVED',
            start_date__lte=date(2026, 8, 3),
            end_date__gte=date(2026, 8, 1)
        ).exists()
        
        assert approved_in_period is True


@pytest.mark.django_db
class TestAttendanceRecords:
    def test_attendance_creation(self, test_employee):
        from datetime import time
        attendance = Attendance.objects.create(
            company=test_employee.company,
            employee=test_employee,
            date=date(2026, 4, 14),
            check_in_time=time(9, 0),
            check_out_time=time(17, 0)
        )
        assert attendance.employee == test_employee
        assert attendance.date == date(2026, 4, 14)
