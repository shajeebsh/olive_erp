import pytest
from datetime import date
from django.test import Client
from django.contrib.auth import get_user_model
from company.models import CompanyProfile
from hr.models import Employee, Department, LeaveRequest, Attendance
from core.models import Role, UserRole
from tests.utils import data_gen, db_helper, logger

User = get_user_model()


@pytest.fixture
def test_company(db):
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
def erp_admin_role(db):
    role, _ = Role.objects.get_or_create(
        name='ErpAdmin',
        defaults={'description': 'ERP Administrator'}
    )
    return role


@pytest.fixture
def admin_user(db, test_company, erp_admin_role):
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
def authenticated_client(admin_user):
    client = Client()
    client.force_login(admin_user)
    return client


@pytest.fixture
def test_department(db, test_company):
    dept, _ = Department.objects.get_or_create(
        company=test_company,
        name='Engineering',
        defaults={'description': 'Engineering Department'}
    )
    return dept


@pytest.fixture
def test_employee(db, admin_user, test_company, test_department):
    employee, _ = Employee.objects.get_or_create(
        user=admin_user,
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


@pytest.fixture
def regular_employee_user(db, test_company):
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
def regular_employee(db, test_company, regular_employee_user, test_department):
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


@pytest.fixture
def sample_department(db, test_company):
    dept_data = data_gen.generate_department_data(test_company)
    dept, _ = Department.objects.get_or_create(
        company=test_company,
        name=dept_data['name'],
        defaults={'description': dept_data['description']}
    )
    return dept


@pytest.fixture
def sample_employee(db, test_company, sample_department):
    user_data = {
        'username': data_gen.generate_username(),
        'email': data_gen.generate_email(),
    }
    user, _ = User.objects.get_or_create(
        username=user_data['username'],
        defaults={'email': user_data['email']}
    )
    user.company = test_company
    user.save()
    
    emp_data = data_gen.generate_employee_data(test_company, sample_department)
    employee, _ = Employee.objects.get_or_create(
        user=user,
        defaults=emp_data
    )
    return employee


@pytest.fixture
def sample_leave_request(db, test_company, test_employee):
    leave_data = data_gen.generate_leave_request_data(test_company, test_employee)
    leave, _ = LeaveRequest.objects.get_or_create(
        company=test_company,
        employee=test_employee,
        start_date=leave_data['start_date'],
        defaults={
            'leave_type': leave_data['leave_type'],
            'end_date': leave_data['end_date'],
            'reason': leave_data['reason'],
            'status': 'PENDING',
        }
    )
    return leave


@pytest.fixture(autouse=True)
def setup_test_logging(request):
    test_name = request.node.name
    module = request.module.__name__ if hasattr(request.module, '__name__') else 'unknown'
    logger.test_start(test_name, module)
    yield
    logger.test_end(test_name)
