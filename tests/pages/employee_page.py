from .base_page import BasePage
from playwright.sync_api import Page
from typing import Optional

class EmployeePage(BasePage):
    LIST_URL = "/hr/employees/"
    CREATE_URL = "/hr/employees/create/"
    EDIT_URL = "/hr/employees/{pk}/edit/"
    
    LOCATORS = {
        'employee_list': 'table.employee-list, table.employees, [data-testid="employee-table"]',
        'employee_row': 'table tbody tr',
        'create_button': 'a[href*="create"], button:has-text("Add Employee"), button:has-text("Create")',
        'employee_id_input': 'input[name="employee_id"], #id_employee_id',
        'first_name_input': 'input[name="first_name"], #id_first_name',
        'last_name_input': 'input[name="last_name"], #id_last_name',
        'email_input': 'input[name="email"], #id_email',
        'department_select': 'select[name="department"], #id_department',
        'job_title_input': 'input[name="job_title"], #id_job_title',
        'hire_date_input': 'input[name="hire_date"], #id_hire_date',
        'salary_input': 'input[name="salary"], #id_salary',
        'phone_input': 'input[name="contact_info"], #id_contact_info',
        'address_input': 'input[name="address"], #id_address',
        'emergency_contact_input': 'input[name="emergency_contact"], #id_emergency_contact',
        'submit_button': 'button[type="submit"], input[type="submit"]',
        'save_button': 'button:has-text("Save"), button:has-text("Update")',
        'cancel_button': 'a:has-text("Cancel"), button:has-text("Cancel")',
        'success_message': '.alert-success, .alert-success:visible',
        'error_message': '.alert-danger, .alert-error, .errorlist',
        'employee_detail': '[data-testid="employee-detail"]',
        'employee_name': 'table tbody tr:first-child td.employee-name, table tbody tr:first-child td:nth-child(2)',
        'employee_department': 'table tbody tr:first-child td.department, table tbody tr:first-child td:nth-child(3)',
        'employee_status': '.status-badge, .employee-status',
        'back_button': 'a:has-text("Back"), a:has-text("Back to List")',
        'filter_input': 'input[type="search"], input[placeholder*="Search"]',
        'pagination': '.pagination, .paginator',
    }
    
    def __init__(self, page: Page, base_url: str = "http://127.0.0.1:8000"):
        super().__init__(page, base_url)
    
    def goto_list(self):
        self.navigate(self.LIST_URL)
        return self
    
    def goto_create(self):
        self.navigate(self.CREATE_URL)
        return self
    
    def goto_edit(self, pk: int):
        self.navigate(self.EDIT_URL.format(pk=pk))
        return self
    
    def click_create(self):
        self.click(self.LOCATORS['create_button'])
        return self
    
    def fill_employee_form(self, **data):
        if 'employee_id' in data:
            self.fill(self.LOCATORS['employee_id_input'], data['employee_id'])
        if 'first_name' in data:
            self.fill(self.LOCATORS['first_name_input'], data['first_name'])
        if 'last_name' in data:
            self.fill(self.LOCATORS['last_name_input'], data['last_name'])
        if 'email' in data:
            self.fill(self.LOCATORS['email_input'], data['email'])
        if 'department' in data:
            self.select_option(self.LOCATORS['department_select'], str(data['department']))
        if 'job_title' in data:
            self.fill(self.LOCATORS['job_title_input'], data['job_title'])
        if 'hire_date' in data:
            self.fill(self.LOCATORS['hire_date_input'], data['hire_date'])
        if 'salary' in data:
            self.fill(self.LOCATORS['salary_input'], str(data['salary']))
        if 'contact_info' in data:
            self.fill(self.LOCATORS['phone_input'], data['contact_info'])
        if 'address' in data:
            self.fill(self.LOCATORS['address_input'], data['address'])
        if 'emergency_contact' in data:
            self.fill(self.LOCATORS['emergency_contact_input'], data['emergency_contact'])
        return self
    
    def submit_form(self):
        self.click(self.LOCATORS['submit_button'])
        self.wait_for_load_state()
        return self
    
    def save(self):
        self.click(self.LOCATORS['save_button'])
        self.wait_for_load_state()
        return self
    
    def cancel(self):
        self.click(self.LOCATORS['cancel_button'])
        return self
    
    def get_success_message(self) -> Optional[str]:
        if self.is_visible(self.LOCATORS['success_message'], timeout=5000):
            return self.get_text(self.LOCATORS['success_message'])
        return None
    
    def get_error_message(self) -> Optional[str]:
        if self.is_visible(self.LOCATORS['error_message'], timeout=5000):
            return self.get_text(self.LOCATORS['error_message'])
        return None
    
    def get_employee_count(self) -> int:
        rows = self.page.locator(self.LOCATORS['employee_row'])
        return rows.count()
    
    def search_employee(self, search_term: str):
        self.fill(self.LOCATORS['filter_input'], search_term)
        self.wait_for_load_state()
        return self
    
    def get_first_employee_name(self) -> Optional[str]:
        if self.is_visible(self.LOCATORS['employee_name'], timeout=5000):
            return self.get_text(self.LOCATORS['employee_name'])
        return None
    
    def is_on_list_page(self) -> bool:
        return self.LIST_URL in self.get_current_url()
    
    def is_on_create_page(self) -> bool:
        return self.CREATE_URL in self.get_current_url()
    
    def is_on_edit_page(self) -> bool:
        return "/edit/" in self.get_current_url()
