import os

import pytest


@pytest.fixture(scope="session")
def test_environment():
    return os.getenv("TEST_ENV", "dev")


@pytest.fixture(scope="session")
def base_url(test_environment):
    if test_environment == "staging":
        return "https://staging.olive-erp.com"
    elif test_environment == "prod":
        return "https://olive-erp.com"
    else:
        return "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def api_base_url(base_url: str):
    return f"{base_url}/api"


@pytest.fixture(scope="session")
def browser_config():
    return {
        "browser": os.getenv("TEST_BROWSER", "chromium"),
        "headless": os.getenv("TEST_HEADLESS", "true").lower() == "true",
        "slowmo": int(os.getenv("TEST_SLOWMO", "0")),
    }


@pytest.fixture(scope="function", autouse=True)
def take_screenshot_on_failure(request):
    yield
    rep_call = getattr(request.node, "rep_call", None)
    if not rep_call or not rep_call.failed:
        return
    if "page" not in getattr(request, "fixturenames", ()):
        return

    os.makedirs("test-results", exist_ok=True)
    test_name = request.node.name
    safe_name = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in test_name)
    page = request.getfixturevalue("page")
    page.screenshot(path=f"test-results/failure-{safe_name}.png")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # This hook helps check if a test failed
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
