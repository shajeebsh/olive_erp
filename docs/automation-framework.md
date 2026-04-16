# OliveERP Automation Framework

## Overview

OliveERP uses a **4-layer test automation framework** for comprehensive testing of UI and API functionality. This architecture ensures maintainability, scalability, and clear separation of concerns across all test implementations.

## Directory Structure

```
olive_erp/
├── test/                           # Automation framework root
│   ├── config/                     # Layer 4 - Configuration
│   │   ├── __init__.py
│   │   ├── settings.py             # Environment-specific settings via python-decouple
│   │   └── conftest.py            # Config-level pytest fixtures
│   ├── utils/                      # Layer 3 - Utilities
│   │   ├── __init__.py
│   │   ├── data_gen.py            # Faker-based dynamic data generation
│   │   ├── db_helper.py           # Django ORM wrappers for test setup
│   │   └── logger.py              # Standardized execution logging
│   ├── pages/                      # Layer 2 - UI Page Objects
│   │   ├── __init__.py
│   │   ├── base_page.py           # BasePage with Playwright wrappers
│   │   ├── employee_page.py       # Employee page object
│   │   ├── leave_page.py          # Leave management page object
│   │   └── dashboard_page.py      # Dashboard page object
│   ├── services/                   # Layer 2 - API Service Objects
│   │   ├── __init__.py
│   │   ├── base_service.py        # Base REST API client
│   │   ├── hr_service.py          # HR module API service
│   │   ├── finance_service.py     # Finance module API service
│   │   ├── inventory_service.py    # Inventory module API service
│   │   └── crm_service.py         # CRM module API service
│   └── test_hr/                    # Layer 1 - Test Layer
│       ├── __init__.py
│       ├── conftest.py             # HR-specific pytest fixtures
│       ├── test_logic.py           # Unit/integration tests
│       └── test_e2e.py            # E2E/browser tests
```

## Layer Architecture

### Layer 1: Test Layer (`test/test_hr/`, `hr/tests/`)

**Purpose**: Declarative test scenarios using pytest.

**Characteristics**:
- No raw locators or business logic
- Only calls to Layer 2 objects and assertions
- Uses `@pytest.mark.django_db` for database access

**Example**:
```python
@pytest.mark.django_db
class TestPayrollLogic:
    def test_payslip_net_calculation_basic(self, test_employee):
        period = PayrollPeriod.objects.create(...)
        payslip = Payslip.objects.create(...)
        assert payslip.net_salary == 5300.00
```

### Layer 2: Business Logic Layer (`test/pages/`, `test/services/`)

#### UI Page Objects (`test/pages/`)

Encapsulate Playwright locators and screen actions. All page objects inherit from `BasePage`.

**Key Methods**:
- `navigate(path)` - Navigate to a URL path
- `click(selector)` - Click an element
- `fill(selector, value)` - Fill form fields
- `select_option(selector, value)` - Select dropdown options
- `get_text(selector)` - Get element text content
- `is_visible(selector)` - Check element visibility
- `wait_for_selector(selector)` - Wait for element state

**Example**:
```python
class EmployeePage(BasePage):
    def __init__(self, page):
        super().__init__(page, base_url=BASE_URL)

    def navigate_to_list(self):
        return self.navigate("/hr/employees/")

    def click_add_employee(self):
        self.click("#add-employee-btn")
        return self

    def fill_employee_form(self, data):
        self.fill("#id_first_name", data['first_name'])
        self.fill("#id_last_name", data['last_name'])
        self.fill("#id_employee_id", data['employee_id'])
        return self
```

#### API Service Objects (`test/services/`)

Encapsulate REST API endpoints and payloads. Support headless API testing without UI.

**Key Methods**:
- `get(endpoint, params)` - GET request
- `post(endpoint, data, json)` - POST request
- `put(endpoint, data, json)` - PUT request
- `patch(endpoint, data, json)` - PATCH request
- `delete(endpoint)` - DELETE request
- `set_auth_token(token)` - Set authentication token
- `is_success(response)` - Check 2xx response
- `is_client_error(response)` - Check 4xx response

**Example**:
```python
class HRService(BaseService):
    def list_employees(self, params=None):
        return self.get("/hr/employees/", params=params)

    def create_employee(self, data):
        return self.post("/hr/employees/", json=data)

    def get_employee(self, employee_id):
        return self.get(f"/hr/employees/{employee_id}/")
```

### Layer 3: Utilities Layer (`test/utils/`)

#### `data_gen.py` - Data Generation

Dynamic test data using `Faker`:

```python
from tests.utils import data_gen

# Generate employee data
employee_data = data_gen.generate_employee_data(company, department)
# Returns: {'employee_id': 'EMP-ABC123', 'job_title': '...', ...}

# Generate leave request data
leave_data = data_gen.generate_leave_request_data(company, employee)

# Generate emails, usernames, addresses
email = data_gen.generate_email()
username = data_gen.generate_username()
```

#### `db_helper.py` - Database Helpers

Django ORM wrappers for efficient test setup:

```python
from tests.utils import db_helper

# Get or create test data
employee = db_helper.get_or_create_employee(company, department)
company = db_helper.get_or_create_company("Test Company Ltd")
```

#### `logger.py` - Execution Logging

Standardized logging for test lifecycle:

```python
from tests.utils import logger

# Log test lifecycle
logger.test_start("test_name", "module_name")
logger.test_end("test_name")

# Log assertions with details
logger.assertion("Expected value", expected, actual, condition)
```

### Layer 4: Configuration Layer (`test/config/`)

#### `settings.py` - Environment Configuration

Uses `python-decouple` for environment-specific settings:

```python
from test.config.settings import settings

BASE_URL = settings.BASE_URL
BROWSER = settings.BROWSER
HEADLESS = settings.HEADLESS
ADMIN_USERNAME = settings.ADMIN_USERNAME
ADMIN_PASSWORD = settings.ADMIN_PASSWORD
```

**Environment Variables**:
| Variable | Default | Description |
|----------|---------|-------------|
| `TEST_ENV` | `dev` | Environment: dev, staging, prod |
| `TEST_BASE_URL` | `http://127.0.0.1:8000` | Base URL for UI tests |
| `TEST_API_BASE_URL` | `http://127.0.0.1:8000/api` | Base URL for API tests |
| `TEST_BROWSER` | `chromium` | Browser: chromium, firefox, webkit |
| `TEST_HEADLESS` | `true` | Run browser headless |
| `TEST_SLOWMO` | `0` | Slow down operations (ms) |
| `TEST_TIMEOUT` | `30000` | Timeout for operations (ms) |
| `TEST_SCREENSHOT_ON_FAILURE` | `true` | Capture screenshot on failure |
| `TEST_LOG_LEVEL` | `INFO` | Logging level |

#### `conftest.py` - Shared Fixtures

Session-scoped fixtures for test configuration:

```python
@pytest.fixture(scope='session')
def test_environment():
    return os.getenv('TEST_ENV', 'dev')

@pytest.fixture(scope='session')
def base_url(test_environment):
    # Returns environment-specific base URL
```

## Test Fixtures

### HR-Specific Fixtures (`test/test_hr/conftest.py`)

| Fixture | Description |
|---------|-------------|
| `test_company` | Creates Test Company Ltd |
| `erp_admin_role` | Creates ErpAdmin role |
| `admin_user` | Admin user for testing |
| `authenticated_client` | Django test client logged in as admin |
| `test_department` | Engineering department |
| `test_employee` | Employee linked to admin user |
| `regular_employee_user` | Regular employee user |
| `regular_employee` | Employee linked to regular user |
| `employee_client` | Client logged in as regular employee |
| `sample_department` | Dynamically generated department |
| `sample_employee` | Employee with generated data |
| `sample_leave_request` | Sample leave request |

## Running Tests

### pytest Commands

```bash
# Run all tests (both new framework and legacy)
python manage.py test

# Run new framework tests only
pytest test/test_hr/

# Run legacy HR tests
pytest hr/tests/

# Run with Playwright UI tests
pytest test/test_hr/ --headed

# Run with slow motion for debugging
pytest test/test_hr/ --slowmo=500

# Run with coverage
pytest --cov=. test/test_hr/

# Run specific test class
pytest test/test_hr/test_logic.py::TestPayrollLogic

# Run specific test
pytest test/test_hr/test_logic.py::TestPayrollLogic::test_payslip_net_calculation_basic
```

### pytest.ini Configuration

```ini
[pytest]
DJANGO_SETTINGS_MODULE = wagtailerp.settings.base
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
testpaths = test/test_hr hr/tests
```

## Dependencies

```txt
pytest>=8.0.0
pytest-django>=4.8.0
playwright>=1.40.0
pytest-playwright>=0.4.0
python-decouple>=3.8
faker>=20.0.0
requests>=2.31.0
allure-pytest>=2.13.0
```

Install with:
```bash
pip install -r requirements_test.txt
playwright install chromium
```

## Migration Pattern

To migrate existing tests to this framework:

1. **Move test files** to appropriate layer (`test/test_hr/`, `test/services/`, etc.)
2. **Replace raw locators** with Page Object calls
3. **Replace direct API calls** with Service Object calls
4. **Use `db_helper`** for test data setup
5. **Use `data_gen`** for dynamic test data
6. **Use `logger`** for execution tracking

## Best Practices

1. **Page Objects**: Never expose raw locators in test code
2. **Service Objects**: Encapsulate all API logic
3. **Fixtures**: Reuse fixtures for consistent test data
4. **Naming**: Use descriptive test names (`test_<what>_<condition>`)
5. **Isolation**: Each test should be independent
6. **Logging**: Use `logger` for debugging and reporting
7. **Screenshots**: Enable `TEST_SCREENSHOT_ON_FAILURE` for debugging

## Architecture Benefits

- **Separation of Concerns**: Each layer has a specific responsibility
- **Maintainability**: Changes in locators only affect Page Objects
- **Reusability**: Services and utilities can be used across test modules
- **Scalability**: Easy to add new modules and test scenarios
- **Readability**: Tests are declarative and self-documenting
