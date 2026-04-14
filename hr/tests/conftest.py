import pytest
from datetime import date
from django.test import Client
from django.contrib.auth import get_user_model
from company.models import CompanyProfile
from hr.models import Employee, Department
from core.models import Role, UserRole

User = get_user_model()


@pytest.fixture
def test_company():
    company, _ = CompanyProfile.objects.get_or_create(
        name="Test Company Ltd",
        defaults={
            'email': 'test@company.com',
            'phone': '1234567890',
            'address': 'Test Address',
            'fiscal_year_start_date': date(2024, 1, 1),
        }
    )
    return company


@pytest.fixture
def erp_admin_role(test_company):
    role, _ = Role.objects.get_or_create(
        name='ErpAdmin',
        defaults={'description': 'ERP Administrator'}
    )
    return role


@pytest.fixture
def test_user(test_company, erp_admin_role):
    user = User.objects.create_user(
        username='testadmin',
        email='admin@testcompany.com',
        password='testpass123'
    )
    user.company = test_company
    user.save()
    
    UserRole.objects.get_or_create(
        user=user,
        role=erp_admin_role,
        company=test_company
    )
    
    return user


@pytest.fixture
def authenticated_client(test_user):
    client = Client()
    client.force_login(test_user)
    return client


@pytest.fixture
def test_department(test_company):
    dept, _ = Department.objects.get_or_create(
        company=test_company,
        name='Engineering',
        defaults={'description': 'Engineering Department'}
    )
    return dept


@pytest.fixture
def test_employee(test_user, test_company, test_department):
    employee, _ = Employee.objects.get_or_create(
        user=test_user,
        defaults={
            'company': test_company,
            'employee_id': 'EMP-TEST-001',
            'department': test_department,
            'job_title': 'Software Developer',
            'hire_date': date(2024, 1, 1),
            'salary': 75000.00,
            'contact_info': 'phone: 1234567890',
            'address': '123 Test Street',
            'emergency_contact': 'Emergency Contact: 0987654321',
        }
    )
    return employee
