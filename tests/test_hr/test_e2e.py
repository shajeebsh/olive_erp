import pytest


def _login(page, base_url: str, username: str, password: str) -> None:
    page.goto(f"{base_url}/accounts/login/", wait_until="domcontentloaded")
    page.fill("#id_username", username)
    page.fill("#id_password", password)
    page.click("button[type='submit']")
    page.wait_for_load_state("domcontentloaded")


@pytest.mark.django_db(transaction=True)
class TestHRE2EBrowser:
    def test_admin_can_open_employee_list(self, page, live_server, transactional_db, admin_user, test_company):
        # Use live_server so the test spins up a real HTTP server for Playwright to drive.
        base_url = live_server.url.rstrip("/")

        _login(page, base_url=base_url, username=admin_user.username, password="testpass123")

        response = page.goto(f"{base_url}/hr/employees/", wait_until="domcontentloaded")
        assert response is not None
        assert response.status < 400

        # Sanity check: we didn't bounce back to the login form.
        assert "/accounts/login/" not in page.url
