from .base_page import BasePage
from playwright.sync_api import Page
from typing import Optional

class DashboardPage(BasePage):
    HR_DASHBOARD_URL = "/hr/"
    MAIN_DASHBOARD_URL = "/"
    
    LOCATORS = {
        'kpi_cards': '.kpi-card, [data-testid="kpi-card"]',
        'kpi_value': '.kpi-value, .kpi-card .value',
        'kpi_label': '.kpi-label, .kpi-card .label',
        'chart_canvas': 'canvas, [data-testid="chart"]',
        'employee_count_kpi': '.kpi-card:has-text("Employee"), .kpi-card:has-text("employee")',
        'leave_count_kpi': '.kpi-card:has-text("Leave"), .kpi-card:has-text("leave")',
        'department_count_kpi': '.kpi-card:has-text("Department"), .kpi-card:has-text("department")',
        'recent_employees_table': 'table.employees, .recent-employees table',
        'recent_leaves_table': 'table.leave-requests, .recent-leaves table',
        'quick_actions': '.quick-actions a, .action-buttons a',
        'filter_period': 'select[name="period"], #id_period',
        'refresh_button': 'button:has-text("Refresh"), button:has-text("Update")',
        'export_button': 'a:has-text("Export"), button:has-text("Export")',
        'notification': '.notification, .alert',
    }
    
    def __init__(self, page: Page, base_url: str = "http://127.0.0.1:8000"):
        super().__init__(page, base_url)
    
    def goto_hr_dashboard(self):
        self.navigate(self.HR_DASHBOARD_URL)
        return self
    
    def goto_main_dashboard(self):
        self.navigate(self.MAIN_DASHBOARD_URL)
        return self
    
    def get_kpi_values(self) -> dict:
        kpi_values = {}
        kpis = self.page.locator(self.LOCATORS['kpi_cards'])
        count = kpis.count()
        for i in range(count):
            card = kpis.nth(i)
            try:
                label = card.locator(self.LOCATORS['kpi_label']).text_content() or ""
                value = card.locator(self.LOCATORS['kpi_value']).text_content() or ""
                kpi_values[label.strip()] = value.strip()
            except:
                pass
        return kpi_values
    
    def get_employee_count(self) -> Optional[int]:
        kpi = self.page.locator(self.LOCATORS['employee_count_kpi'])
        if kpi.count() > 0:
            try:
                value_text = kpi.locator(self.LOCATORS['kpi_value']).text_content()
                return int(value_text.strip()) if value_text else None
            except:
                return None
        return None
    
    def get_leave_count(self) -> Optional[int]:
        kpi = self.page.locator(self.LOCATORS['leave_count_kpi'])
        if kpi.count() > 0:
            try:
                value_text = kpi.locator(self.LOCATORS['kpi_value']).text_content()
                return int(value_text.strip()) if value_text else None
            except:
                return None
        return None
    
    def has_charts(self) -> bool:
        return self.is_visible(self.LOCATORS['chart_canvas'], timeout=3000)
    
    def refresh_dashboard(self):
        self.click(self.LOCATORS['refresh_button'])
        self.wait_for_load_state()
        return self
    
    def get_recent_employees(self) -> list:
        table = self.page.locator(self.LOCATORS['recent_employees_table'])
        employees = []
        if table.count() > 0:
            rows = table.locator('tbody tr')
            for i in range(min(rows.count(), 10)):
                row = rows.nth(i)
                cells = row.locator('td')
                if cells.count() > 0:
                    employees.append({
                        'name': cells.nth(0).text_content() or "",
                        'department': cells.nth(1).text_content() if cells.count() > 1 else "",
                    })
        return employees
    
    def get_notification_message(self) -> Optional[str]:
        if self.is_visible(self.LOCATORS['notification'], timeout=3000):
            return self.get_text(self.LOCATORS['notification'])
        return None
    
    def is_on_hr_dashboard(self) -> bool:
        return self.HR_DASHBOARD_URL in self.get_current_url() or "/hr" in self.get_current_url()
