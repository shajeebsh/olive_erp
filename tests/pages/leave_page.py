from .base_page import BasePage
from playwright.sync_api import Page
from typing import Optional

class LeavePage(BasePage):
    LIST_URL = "/hr/leave/"
    CREATE_URL = "/hr/leave/create/"
    EDIT_URL = "/hr/leave/{pk}/"
    
    LOCATORS = {
        'leave_list': 'table.leave-list, table.leave-requests, [data-testid="leave-table"]',
        'leave_row': 'table tbody tr',
        'create_button': 'a[href*="leave/create"], button:has-text("Request Leave"), button:has-text("New Leave")',
        'leave_type_select': 'select[name="leave_type"], #id_leave_type',
        'start_date_input': 'input[name="start_date"], #id_start_date',
        'end_date_input': 'input[name="end_date"], #id_end_date',
        'reason_textarea': 'textarea[name="reason"], #id_reason',
        'submit_button': 'button[type="submit"], input[type="submit"]',
        'save_button': 'button:has-text("Save"), button:has-text("Update")',
        'approve_button': 'button:has-text("Approve"), a:has-text("Approve")',
        'reject_button': 'button:has-text("Reject"), a:has-text("Reject")',
        'cancel_button': 'a:has-text("Cancel"), button:has-text("Cancel")',
        'success_message': '.alert-success, .messages .alert-success',
        'error_message': '.alert-danger, .alert-error, .errorlist',
        'status_badge': '.status-badge, .leave-status',
        'back_button': 'a:has-text("Back"), a:has-text("Back to List")',
        'filter_status': 'select[name="status"], #id_status',
        'filter_type': 'select[name="leave_type"], #id_leave_type',
        'pagination': '.pagination, .paginator',
        'no_records': '.empty, .no-records, td:has-text("No")',
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
    
    def fill_leave_form(self, leave_type: str = None, start_date: str = None, 
                        end_date: str = None, reason: str = None):
        if leave_type:
            self.select_option(self.LOCATORS['leave_type_select'], leave_type)
        if start_date:
            self.fill(self.LOCATORS['start_date_input'], start_date)
        if end_date:
            self.fill(self.LOCATORS['end_date_input'], end_date)
        if reason:
            self.fill(self.LOCATORS['reason_textarea'], reason)
        return self
    
    def submit_form(self):
        self.click(self.LOCATORS['submit_button'])
        self.wait_for_load_state()
        return self
    
    def approve_leave(self, pk: int = None):
        if pk:
            self.goto_edit(pk)
        self.click(self.LOCATORS['approve_button'])
        self.wait_for_load_state()
        return self
    
    def reject_leave(self, pk: int = None):
        if pk:
            self.goto_edit(pk)
        self.click(self.LOCATORS['reject_button'])
        self.wait_for_load_state()
        return self
    
    def get_success_message(self) -> Optional[str]:
        if self.is_visible(self.LOCATORS['success_message'], timeout=5000):
            return self.get_text(self.LOCATORS['success_message'])
        return None
    
    def get_error_message(self) -> Optional[str]:
        if self.is_visible(self.LOCATORS['error_message'], timeout=5000):
            return self.get_text(self.LOCATORS['error_message'])
        return None
    
    def get_leave_count(self) -> int:
        rows = self.page.locator(self.LOCATORS['leave_row'])
        return rows.count()
    
    def filter_by_status(self, status: str):
        self.select_option(self.LOCATORS['filter_status'], status)
        self.wait_for_load_state()
        return self
    
    def filter_by_type(self, leave_type: str):
        self.select_option(self.LOCATORS['filter_type'], leave_type)
        self.wait_for_load_state()
        return self
    
    def has_leave_records(self) -> bool:
        return not self.is_visible(self.LOCATORS['no_records'], timeout=3000)
    
    def is_on_list_page(self) -> bool:
        return self.LIST_URL in self.get_current_url()
