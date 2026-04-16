import uuid
from datetime import date, datetime, timedelta
from faker import Faker

fake = Faker(['en_US', 'en_GB'])

class DataGenerator:
    @staticmethod
    def generate_employee_id():
        return f"EMP-{uuid.uuid4().hex[:8].upper()}"
    
    @staticmethod
    def generate_username(first_name=None, last_name=None):
        fn = first_name or fake.first_name()
        ln = last_name or fake.last_name()
        return f"{fn.lower()}.{ln.lower()}{uuid.uuid4().hex[:4]}"
    
    @staticmethod
    def generate_email(first_name=None, last_name=None, domain=None):
        fn = first_name or fake.first_name()
        ln = last_name or fake.last_name()
        d = domain or fake.domain_name()
        return f"{fn.lower()}.{ln.lower()}@{d}"
    
    @staticmethod
    def generate_phone():
        return fake.phone_number()
    
    @staticmethod
    def generate_address():
        return fake.street_address()
    
    @staticmethod
    def generate_department_name():
        departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 
                      'Operations', 'IT', 'Support', 'R&D', 'Legal']
        return fake.random_element(departments) + f" {fake.random_int(1, 99)}"
    
    @staticmethod
    def generate_job_title():
        titles = ['Software Engineer', 'Sales Manager', 'Marketing Specialist',
                  'HR Coordinator', 'Financial Analyst', 'Project Manager',
                  'Data Analyst', 'Customer Support', 'Product Manager', 'Designer']
        return fake.random_element(titles)
    
    @staticmethod
    def generate_salary(min_val=30000, max_val=150000):
        import random
        return round(random.uniform(min_val, max_val), 2)
    
    @staticmethod
    def generate_date(start_date=None, end_date=None):
        if not start_date:
            start_date = date(2020, 1, 1)
        if not end_date:
            end_date = date.today()
        delta_days = (end_date - start_date).days
        random_days = fake.random_int(0, delta_days)
        return start_date + timedelta(days=random_days)
    
    @staticmethod
    def generate_future_date(days_ahead=30):
        return date.today() + timedelta(days=fake.random_int(1, days_ahead))
    
    @staticmethod
    def generate_leave_type():
        return fake.random_element(['VACATION', 'SICK', 'PERSONAL', 'MATERNITY', 'PATERNITY'])
    
    @staticmethod
    def generate_leave_reason():
        reasons = [
            'Family vacation',
            'Medical appointment',
            'Personal matter',
            'Home renovation',
            'Wedding attendance',
            'Emergency situation',
            'Annual leave',
            'Sick leave',
        ]
        return fake.random_element(reasons)
    
    @staticmethod
    def generate_department_data(company):
        return {
            'company': company,
            'name': DataGenerator.generate_department_name(),
            'description': fake.sentence(nb_words=6),
        }
    
    @staticmethod
    def generate_employee_data(company, department=None):
        first_name = fake.first_name()
        last_name = fake.last_name()
        return {
            'company': company,
            'employee_id': DataGenerator.generate_employee_id(),
            'department': department,
            'job_title': DataGenerator.generate_job_title(),
            'hire_date': DataGenerator.generate_date(date(2018, 1, 1), date(2025, 12, 31)),
            'salary': DataGenerator.generate_salary(),
            'contact_info': f"phone: {DataGenerator.generate_phone()}",
            'address': DataGenerator.generate_address(),
            'emergency_contact': f"Emergency: {DataGenerator.generate_phone()}",
        }
    
    @staticmethod
    def generate_leave_request_data(company, employee):
        start = DataGenerator.generate_future_date(60)
        duration = fake.random_int(1, 10)
        return {
            'company': company,
            'employee': employee,
            'leave_type': DataGenerator.generate_leave_type(),
            'start_date': start,
            'end_date': start + timedelta(days=duration),
            'reason': DataGenerator.generate_leave_reason(),
        }

data_gen = DataGenerator()
