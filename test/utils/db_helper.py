from datetime import date
from django.contrib.auth import get_user_model
from company.models import CompanyProfile
from hr.models import Employee, Department, LeaveRequest, Attendance
from core.models import Role, UserRole
from finance.models import Account, JournalEntry, Invoice
from inventory.models import Product, Warehouse, StockLevel
from crm.models import Customer, Lead, SalesOrder
from django.db import transaction

User = get_user_model()

class DBHelper:
    @staticmethod
    def get_or_create_company(name="Test Company Ltd", **kwargs):
        defaults = {
            'email': kwargs.get('email', 'test@company.com'),
            'phone': kwargs.get('phone', '1234567890'),
            'address': kwargs.get('address', 'Test Address'),
            'fiscal_year_start_date': kwargs.get('fiscal_year_start_date', date(2024, 1, 1)),
        }
        return CompanyProfile.objects.get_or_create(name=name, defaults=defaults)
    
    @staticmethod
    def get_or_create_role(name, description=None):
        return Role.objects.get_or_create(
            name=name,
            defaults={'description': description or f'{name} role'}
        )
    
    @staticmethod
    def get_or_create_user(username, company, email=None, password=None, role_name=None):
        defaults = {
            'email': email or f'{username}@testcompany.com',
            'first_name': username.split('.')[0] if '.' in username else username,
        }
        if password:
            user, created = User.objects.get_or_create(
                username=username,
                defaults=defaults
            )
            if created:
                user.set_password(password)
                user.save()
        else:
            user, created = User.objects.get_or_create(username=username, defaults=defaults)
        
        user.company = company
        user.save()
        
        if role_name:
            role, _ = DBHelper.get_or_create_role(role_name)
            UserRole.objects.get_or_create(user=user, role=role, company=company)
        
        return user
    
    @staticmethod
    def get_or_create_department(company, name, description=None):
        return Department.objects.get_or_create(
            company=company,
            name=name,
            defaults={'description': description or f'{name} department'}
        )
    
    @staticmethod
    def get_or_create_employee(user, company, department=None, **kwargs):
        defaults = {
            'company': company,
            'department': department,
            'employee_id': kwargs.get('employee_id', f'EMP-{user.username.upper()}'),
            'job_title': kwargs.get('job_title', 'Test Employee'),
            'hire_date': kwargs.get('hire_date', date(2024, 1, 1)),
            'salary': kwargs.get('salary', 50000.00),
            'contact_info': kwargs.get('contact_info', 'phone: 1234567890'),
            'address': kwargs.get('address', '123 Test Street'),
            'emergency_contact': kwargs.get('emergency_contact', 'Emergency: 0987654321'),
        }
        if department:
            defaults['department'] = department
        return Employee.objects.get_or_create(user=user, defaults=defaults)
    
    @staticmethod
    def get_or_create_leave_request(company, employee, leave_type='VACATION', 
                                     start_date=None, end_date=None, reason='Test leave',
                                     status='PENDING'):
        if not start_date:
            start_date = date.today()
        if not end_date:
            end_date = start_date
        return LeaveRequest.objects.get_or_create(
            company=company,
            employee=employee,
            defaults={
                'leave_type': leave_type,
                'start_date': start_date,
                'end_date': end_date,
                'reason': reason,
                'status': status,
            }
        )
    
    @staticmethod
    def get_or_create_account(company, code, name, account_type='ASSET'):
        return Account.objects.get_or_create(
            company=company,
            code=code,
            defaults={
                'name': name,
                'account_type': account_type,
                'is_active': True,
            }
        )
    
    @staticmethod
    def get_or_create_customer(company, name=None, email=None):
        from faker import Faker
        fake = Faker()
        return Customer.objects.get_or_create(
            company=company,
            name=name or fake.company(),
            defaults={
                'email': email or fake.email(),
                'phone': fake.phone_number(),
                'address': fake.street_address(),
            }
        )
    
    @staticmethod
    def get_or_create_product(company, name=None, sku=None):
        from faker import Faker
        fake = Faker()
        return Product.objects.get_or_create(
            company=company,
            sku=sku or fake.uuid4()[:8].upper(),
            defaults={
                'name': name or fake.catch_phrase(),
                'description': fake.text(max_nb_chars=100),
                'unit_price': round(fake.pydecimal(left_digits=4, right_digits=2, positive=True), 2),
            }
        )
    
    @staticmethod
    def cleanup_test_data(company):
        with transaction.atomic():
            LeaveRequest.objects.filter(company=company).delete()
            Attendance.objects.filter(company=company).delete()
            Employee.objects.filter(company=company).delete()
            Department.objects.filter(company=company).delete()
            UserRole.objects.filter(company=company).delete()
            User.objects.filter(company=company).delete()

db_helper = DBHelper()
