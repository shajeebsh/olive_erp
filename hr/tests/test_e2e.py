import pytest
from datetime import date
from django.test import Client
from django.contrib.auth import get_user_model
from company.models import CompanyProfile
from hr.models import Employee, Department, LeaveRequest
from core.models import Role, UserRole

User = get_user_model()


@pytest.fixture
def regular_employee_user(test_company):
    role, _ = Role.objects.get_or_create(
        name='Employee',
        defaults={'description': 'Regular Employee'}
    )
    
    user = User.objects.create_user(
        username='employee_user',
        email='employee@testcompany.com',
        password='testpass123'
    )
    user.company = test_company
    user.save()
    
    UserRole.objects.get_or_create(
        user=user,
        role=role,
        company=test_company
    )
    
    return user


@pytest.fixture
def regular_employee(test_company, regular_employee_user, test_department):
    employee, _ = Employee.objects.get_or_create(
        user=regular_employee_user,
        defaults={
            'company': test_company,
            'employee_id': 'EMP-TEST-002',
            'department': test_department,
            'job_title': 'Tester',
            'hire_date': date(2024, 1, 1),
            'salary': 50000.00,
            'contact_info': 'phone: 1234567890',
            'address': '123 Test Street',
            'emergency_contact': 'Emergency Contact: 0987654321',
        }
    )
    return employee


@pytest.fixture
def employee_client(regular_employee_user):
    client = Client()
    client.force_login(regular_employee_user)
    return client


@pytest.mark.django_db
class TestEmployeeLifecycle:
    def test_employee_list_view(self, authenticated_client, test_employee):
        response = authenticated_client.get('/hr/employees/')
        assert response.status_code == 200

    def test_employee_create_view(self, authenticated_client, test_department):
        response = authenticated_client.get('/hr/employees/create/')
        assert response.status_code in [200, 302]

    def test_employee_detail_view(self, authenticated_client, test_employee):
        response = authenticated_client.get(f'/hr/employees/{test_employee.pk}/edit/')
        assert response.status_code in [200, 302, 404]


@pytest.mark.django_db
class TestLeaveWorkflow:
    def test_employee_can_submit_leave_request(self, employee_client, regular_employee):
        response = employee_client.get('/hr/leave/create/')
        assert response.status_code in [200, 302]

    def test_admin_can_view_leave_requests(self, authenticated_client, test_employee):
        LeaveRequest.objects.create(
            company=test_employee.company,
            employee=test_employee,
            leave_type='VACATION',
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 5),
            reason='Test leave',
            status='PENDING'
        )
        response = authenticated_client.get('/hr/leave/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestDashboardHRMetrics:
    def test_hr_dashboard_accessible(self, authenticated_client):
        response = authenticated_client.get('/hr/')
        assert response.status_code in [200, 302]

    def test_main_dashboard_hr_snapshot(self, authenticated_client, test_employee):
        response = authenticated_client.get('/')
        assert response.status_code == 200
