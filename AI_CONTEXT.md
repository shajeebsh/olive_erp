# AI_CONTEXT.md

## 1. Project Overview

OliveERP is a comprehensive, modular Enterprise Resource Planning (ERP) system built with Django and Wagtail CMS. It provides full double-entry accounting, inventory management, CRM/sales, purchasing/procurement, HR, project management, and tax compliance features with a modern Bootstrap-based UI.

**Target users**: Small to medium businesses requiring an all-in-one ERP solution with accounting, operations, and compliance capabilities.

**Development stage**: In-progress / MVP - core modules are functional but some areas (like accounting reporting) are being enhanced.

---

## 2. Tech Stack

- **Backend**: Python 3.11+, Django 4.2 LTS, Wagtail CMS 5.2+
- **Frontend**: Django Templates, Bootstrap 5, **HTMX** (used for inline editing in bank reconciliation table, live tax previews), Chart.js
- **Database**: MySQL (production) / SQLite (dev)
- **Task Queue**: Celery with Redis
- **Authentication**: Custom User model in `core/models.py`
- **Key Libraries**:
  - `djangorestframework` - REST API
  - `django-environ`, `python-decouple` - Configuration
  - `celery`, `redis` - Background tasks
  - `django-modeltranslation` - i18n
  - `weasyprint`, `reportlab` - PDF generation
  - `django-htmx` - HTMX integration
  - `Pillow` - Image processing
  - `pandas`, `openpyxl` - Data/Excel
  - `faker` - Sample data generation
  - `dj-database-url` - Database URL parsing
  - `psycopg2-binary` - PostgreSQL driver

---

## 3. Architecture & Key Design Decisions

### Architecture Pattern
- **Modular Monolith** - Django apps organized by business domain (finance, inventory, crm, hr, etc.)
- **MVC** - Models in each app, views in `views.py`, URLs in `urls.py`
- **Signal-driven** - Django signals for automated workflows (inventory updates, invoice generation)

### Folder Structure
```
olive_erp/
├── apps/accounting/         # Extended accounting (assets, compliance, reconciliation)
├── core/                    # Custom User, mixins, tasks, context processors
├── company/                 # CompanyProfile (singleton), Currency
├── finance/                 # Account, JournalEntry, Invoice
├── inventory/               # Product, Warehouse, StockLevel, StockMovement
├── crm/                     # Customer, SalesOrder
├── hr/                      # Employee, Department, LeaveRequest
├── projects/                # Project, Task
├── purchasing/              # Supplier, PurchaseOrder, GoodsReceivedNote
├── reporting/               # Report definitions, exports
├── tax_engine/              # Tax periods, filings (IE, UK, IN, AE)
├── templates/               # Django templates
├── static/                  # CSS, JS, images
├── wagtailerp/              # Django settings
```

### Key Design Decisions
- **Company Scoping**: Most modules scope data by `CompanyProfile` via ForeignKey
- **Custom User**: Uses `core.User` (extends AbstractUser) with optional company link
- **Navigation**: Generated via `core.context_processors.navigation_menu`
- **Accounting**: Uses `finance.Account`, `JournalEntry`, `JournalEntryLine` as source of truth
- **Accounting Extensions**: `apps.accounting/*` adds specialized features (fixed assets, bank reconciliation)
- **Custom Signals**: `finance/signals.py` defines `journal_entry_posted` signal, emitted from `JournalEntry.post()`, with receivers in `core/signals.py` (budget updates, reconciliation invalidation, VAT threshold checks) and `apps/accounting/*/signals.py`
- **Tax Engine Registry**: `tax_engine` uses registry pattern (`BaseTaxEngine`) for multi-country tax compliance
- **UI Layout**: Top navigation layout (not sidebar) - see templates/base.html, static/css/olive-theme.css, static/js/navigation.js

---

## 4. Module / Feature Breakdown

| Module | Description | Key Files |
|--------|-------------|-----------|
| **core** | Custom User model, tasks, context processors | `core/models.py`, `core/tasks.py`, `core/context_processors.py` |
| **company** | Singleton CompanyProfile, Currency | `company/models.py` |
| **finance** | Chart of accounts, journal entries, invoices, budgets | `finance/models.py`, `finance/views.py` |
| **inventory** | Products, categories, warehouses, stock levels/movements | `inventory/models.py` |
| **crm** | Customers, sales orders, quotations | `crm/models.py` |
| **hr** | Employees, departments, leave requests, attendance | `hr/models.py` |
| **projects** | Projects and tasks | `projects/models.py` |
| **purchasing** | Suppliers, purchase orders, GRNs | `purchasing/models.py` |
| **reporting** | Report definitions and exports | `reporting/models.py`, `reporting/services.py` |
| **dashboard** | Dashboard KPIs | `dashboard/views.py` |
| **tax_engine** (formerly compliance) | Tax periods, filings, RBO for IE/UK/IN/AE (uses registry pattern) | `tax_engine/base/models.py`, `tax_engine/countries/` |
| **apps.accounting** | Extended accounting (fixed assets, reconciliation, compliance); statutory registers (Directors, Members, Beneficial Owners) registered as Wagtail snippets in `apps/accounting/statutory/wagtail_hooks.py` | `apps/accounting/*/models.py` |

---

## 5. Current State

### ✅ Completed Features
- User authentication with custom User model
- Company profile with currencies
- Finance: Chart of accounts, journal entries, invoices
- Inventory: Products, warehouses, stock tracking
- CRM: Customers, sales orders
- HR: Employees, departments, leave, attendance
- Projects: Project/task management
- Purchasing: Suppliers, POs, GRNs
- Tax engine: Tax periods, filings, RBO for multiple countries
- Basic accounting reports (P&L, Balance Sheet)
- Fixed assets management
- Bank reconciliation
- Dividend register
- **UI with polished top navigation layout** - Horizontal app shell with dropdowns, search, user dropdown

### 🔄 In-progress Features
- **Top navigation UI polish**: Completed major CSS/styling improvements, refined horizontal layout, dropdowns, mobile responsiveness
- **Accounting module**: Enhanced reporting, seed data, compliance features
- **Test coverage**: Test discovery for `apps.accounting` module
- **Related party transactions**: Consolidation between two models in progress

### ❌ Not Yet Started
- Full audit trail implementation
- Multi-company support (current design is single-company per installation)
- Advanced workflow automation beyond signals
- API documentation

### Optional / Workarounds
- **Accounting seed data**: Use `python manage.py generate_sample_data` to populate accounting tables (required after migrations on fresh DB)
- **Testing accounting**: Run tests with `python manage.py test apps.accounting.tests.test_models`
- **Multi-country tax**: The `tax_engine` uses registry pattern (`BaseTaxEngine`) - each country implements the abstract base class

---

## 6. Known Issues & Workarounds

1. **Accounting tables missing**: `apps.accounting_*` tables don't exist in SQLite - need migrations for MySQL/PostgreSQL
   - Tables: `apps_accounting_fixedasset`, `apps_accounting_bankreconciliation`, etc.
   - Migrations exist but table creation may fail on SQLite

2. **Test discovery**: `manage.py test apps.accounting` may fail if subdirectories lack `__init__.py`
   - Ensure every subdirectory under `apps/accounting/` has an `__init__.py` file
   - Then run: `python manage.py test apps.accounting`

3. **Duplicate `get_user_company()` helper**: The helper is currently duplicated in:
   - `apps/accounting/reporting/views.py`
   - `apps/accounting/assets/views.py`
   - **TODO**: Centralize in `core/utils.py`

4. **Duplicate RelatedPartyTransaction**: Two models exist:
   - `apps/accounting/compliance/models.py::RelatedPartyTransaction` (standalone)
   - `apps/accounting/related_party/models.py::RelatedPartyTransaction` (journal-linked)
   - Views query both but data should be consolidated

5. **Sample data company mismatch**: Old seed data creates "Olive Tech Solutions Ltd" but current user may be linked to "Nimra tech"
   - Use `manage.py reset_demo_data` to get clean dataset

---

## 7. Data Models & Key Entities

### Core Entities
- **User** (`core.User`) - Custom user with optional `company` FK
- **CompanyProfile** (`company.CompanyProfile`) - Singleton company settings, currency, VAT registration
- **Currency** (`company.Currency`) - Currency codes and exchange rates

### Finance Entities
- **Account** (`finance.Account`) - Chart of accounts with hierarchical structure
- **JournalEntry** (`finance.JournalEntry`) - Posted accounting transactions
- **JournalEntryLine** (`finance.JournalEntryLine`) - Individual debit/credit lines
- **Invoice** (`finance.Invoice`) - Customer invoices

### Inventory Entities
- **Product** (`inventory.Product`) - Product master with pricing
- **Warehouse** (`inventory.Warehouse`) - Storage locations
- **StockLevel** (`inventory.StockLevel`) - Current stock per product/warehouse
- **StockMovement** (`inventory.StockMovement`) - Stock history

### Accounting Extensions
- **FixedAsset** (`apps/accounting/assets/models.py`) - Asset tracking with depreciation
- **BankReconciliation** (`apps/accounting/reconciliation/models.py`) - Bank reconciliation periods
- **Dividend** (`apps/accounting/compliance/models.py`) - Dividend records
- **CT1Computation** (`apps/accounting/compliance/models.py`) - Corporation tax computation
- **ComplianceDeadline** (`apps/accounting/compliance/models.py`) - Compliance deadlines

### Tax Engine
- **TaxPeriod** (`tax_engine/base/models.py`) - Tax reporting periods
- **TaxFiling** (`tax_engine/base/models.py`) - Tax filing records
- **BeneficialOwner** (`tax_engine/countries/ie/rbo.py`) - Irish RBO registrations

---

## 8. External Integrations & Environment

### Required Environment Variables
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode
- `DATABASE_URL` - Database connection (MySQL/PostgreSQL)
- `REDIS_URL` - Redis connection for Celery
- `EMAIL_*` - Email configuration
- `WAGTAIL_*` - Wagtail settings

### Celery Beat Schedule
- Celery Beat schedules are defined in `wagtailerp/settings/base.py` under `CELERY_BEAT_SCHEDULE` (may be overridden in environment-specific settings files)
- Example: daily invoice generation, nightly stock valuations

### Third-Party Services
- **Wagtail CMS** - Content management and admin panels
- **Chart.js** - Dashboard visualizations
- **HTMX** - Partial page updates
- **WeasyPrint/ReportLab** - PDF generation
- **Bootstrap 5** - UI framework

---

## 9. What NOT to Change

1. **Company scoping pattern**: Don't remove `company` FK from models - it's fundamental to multi-tenant design
2. **Account model**: `finance.Account` is the source of truth for accounting - don't duplicate
3. **Navigation via context processor**: `core.context_processors.navigation_menu` generates all nav items - modify there, not hardcoded
4. **Signal workflows**: `core/signals.py` handles automatic inventory/invoice updates - be careful modifying
5. **Custom User model**: Must use `core.User` - don't switch to default Django user
6. **Top navigation layout**: The polished top-nav layout in `templates/base.html` with CSS in `static/css/olive-theme.css` must be preserved - do not revert to left sidebar

---

## 10. Conventions & Coding Standards

### Naming Conventions
- **Models**: PascalCase (`CompanyProfile`, `JournalEntry`)
- **Views**: PascalCase with suffix (`ProfitAndLossView`, `FixedAssetListView`)
- **URL names**: `module:view_name` (e.g., `accounting:profit_loss`)
- **Templates**: lowercase with underscores (`profit_loss.html`)
- **CSS classes**: kebab-case (`.sidebar-container`, `.nav-module-link`)

### File Organization
- Models in `models.py`
- Views in `views.py`
- Forms in `forms.py`
- URLs in `urls.py`
- Admin in `admin.py`
- Templates in `app_name/template_path/`
- Static in `static/app_name/`

### Code Style
- Use `gettext_lazy` for translations
- Use `DecimalField` for money fields
- Include `created_at` and `updated_at` on all models
- Use `LoginRequiredMixin` on all views
- Type hints on public methods

---

## 11. Next Logical Steps

1. **Complete accounting module migrations**: Run migrations for `apps.accounting` on production database to create missing tables
2. **Consolidate RelatedPartyTransaction**: Choose one model as source of truth and migrate data
3. **Add more accounting forms/views**: Create forms for creating/editing fixed assets, dividends, etc.
4. **Improve test coverage**: Add more tests for `apps.accounting` and other modules
5. **API development**: Expose key entities via DRF for potential mobile/web apps
6. **Audit trail**: Implement full audit logging for financial transactions
7. **UI refinements**: Continue to iterate on the top navigation based on user feedback

## 12. UI Implementation Notes (April 2025)

### Top Navigation Implementation
- **Layout**: Fixed top header, 64px height, gradient olive theme
- **Structure**: Brand (left) → Module nav (center) → Search + User (right)
- **Files**:
  - `templates/base.html` - Main shell with top-navbar
  - `static/css/olive-theme.css` - All top navigation styles (378 lines)
  - `static/js/navigation.js` - Mobile toggle, dropdowns, search handling
  - `static/css/mobile.css` - Responsive overrides (simplified, sidebar refs removed)
- **Features**:
  - Horizontal scrollable module links on smaller screens
  - Hover dropdowns on desktop, stacked accordion on mobile
  - Search with expandable input and results dropdown
  - User avatar + name + dropdown for settings/logout
  - Active state highlighting based on current URL
  - Smooth transitions and hover effects
  - Mobile hamburger menu with X close icon

### Deprecations
- `templates/includes/sidebar.html` - No longer primary nav (retained for reference)
- `templates/includes/topbar.html` - No longer used (absorbed into base.html)
- Old sidebar CSS classes in olive-theme.css - Removed
