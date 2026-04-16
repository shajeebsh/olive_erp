from playwright.sync_api import Page, expect
from typing import Optional, Union
import allure

class BasePage:
    def __init__(self, page: Page, base_url: str = "http://127.0.0.1:8000"):
        self.page = page
        self.base_url = base_url
    
    def navigate(self, path: str, wait_until: str = "domcontentloaded"):
        url = f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}"
        self.page.goto(url, wait_until=wait_until)
        self.wait_for_load_state()
        return self
    
    def navigate_to_url(self, url: str, wait_until: str = "domcontentloaded"):
        self.page.goto(url, wait_until=wait_until)
        self.wait_for_load_state()
        return self
    
    def click(self, selector: str, timeout: int = 30000):
        self.page.click(selector, timeout=timeout)
        self.wait_for_load_state()
        return self
    
    def dblclick(self, selector: str, timeout: int = 30000):
        self.page.dblclick(selector, timeout=timeout)
        return self
    
    def fill(self, selector: str, value: str, timeout: int = 30000):
        self.page.fill(selector, value, timeout=timeout)
        return self
    
    def type_text(self, selector: str, text: str, delay: int = 0, timeout: int = 30000):
        self.page.type_(selector, text, delay=delay, timeout=timeout)
        return self
    
    def select_option(self, selector: str, value: str, timeout: int = 30000):
        self.page.select_option(selector, value, timeout=timeout)
        return self
    
    def check(self, selector: str, timeout: int = 30000):
        self.page.check(selector, timeout=timeout)
        return self
    
    def uncheck(self, selector: str, timeout: int = 30000):
        self.page.uncheck(selector, timeout=timeout)
        return self
    
    def get_text(self, selector: str, timeout: int = 30000) -> str:
        return self.page.text_content(selector, timeout=timeout) or ""
    
    def get_attribute(self, selector: str, attribute: str, timeout: int = 30000) -> Optional[str]:
        return self.page.get_attribute(selector, attribute, timeout=timeout)
    
    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
        except:
            return False
    
    def is_hidden(self, selector: str, timeout: int = 5000) -> bool:
        try:
            self.page.wait_for_selector(selector, state="hidden", timeout=timeout)
            return True
        except:
            return False
    
    def is_enabled(self, selector: str, timeout: int = 5000) -> bool:
        return self.page.is_enabled(selector, timeout=timeout)
    
    def wait_for_selector(self, selector: str, state: str = "visible", timeout: int = 30000):
        self.page.wait_for_selector(selector, state=state, timeout=timeout)
        return self
    
    def wait_for_load_state(self, state: str = "domcontentloaded"):
        self.page.wait_for_load_state(state)
        return self
    
    def wait_for_url(self, url_pattern: str, timeout: int = 30000):
        self.page.wait_for_url(url_pattern, timeout=timeout)
        return self
    
    def wait_for_response(self, url_pattern: str, timeout: int = 30000):
        return self.page.wait_for_response(url_pattern, timeout=timeout)
    
    def screenshot(self, path: str, full_page: bool = False):
        self.page.screenshot(path=path, full_page=full_page)
        return self
    
    def get_current_url(self) -> str:
        return self.page.url
    
    def get_title(self) -> str:
        return self.page.title()
    
    def reload(self):
        self.page.reload()
        self.wait_for_load_state()
        return self
    
    def go_back(self):
        self.page.go_back()
        self.wait_for_load_state()
        return self
    
    def go_forward(self):
        self.page.go_forward()
        self.wait_for_load_state()
        return self
    
    def expect_element(self, selector: str, state: str = "visible"):
        return expect(self.page.locator(selector)).to_be_visible() if state == "visible" else expect(self.page.locator(selector)).to_be_hidden()
    
    def expect_url(self, url_pattern: str):
        return expect(self.page).to_have_url(url_pattern)
    
    def expect_title(self, title: str):
        return expect(self.page).to_have_title(title)
    
    def handle_dialog(self, accept: bool = True, prompt_text: str = None):
        def dialog_handler(dialog):
            if prompt_text:
                dialog.accept(prompt_text)
            elif accept:
                dialog.accept()
            else:
                dialog.dismiss()
        self.page.on("dialog", dialog_handler)
        return self
    
    @property
    def viewport(self):
        return self.page.viewport_size
