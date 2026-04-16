import pytest
import os
from pathlib import Path

@pytest.fixture(scope='session')
def test_environment():
    return os.getenv('TEST_ENV', 'dev')

@pytest.fixture(scope='session')
def base_url(test_environment):
    if test_environment == 'staging':
        return 'https://staging.olive-erp.com'
    elif test_environment == 'prod':
        return 'https://olive-erp.com'
    else:
        return 'http://127.0.0.1:8000'

@pytest.fixture(scope='session')
def api_base_url(test_environment):
    return f"{base_url if 'base_url' in dir() else 'http://127.0.0.1:8000'}/api"

@pytest.fixture(scope='session')
def browser_config():
    return {
        'browser': os.getenv('TEST_BROWSER', 'chromium'),
        'headless': os.getenv('TEST_HEADLESS', 'true').lower() == 'true',
        'slowmo': int(os.getenv('TEST_SLOWMO', '0')),
    }

@pytest.fixture(scope='function')
def take_screenshot_on_failure(page):
    yield page
    if hasattr(pytest, 'exception'):
        page.screenshot(path=f'test-results/failure-{page.title}.png')
