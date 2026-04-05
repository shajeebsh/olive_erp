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

## 12. UI Implementation Notes

### Two-Row Enterprise Header (April 2026)
- **Layout**: Two fixed header rows - utility bar (56px) + navigation bar (48px), total 104px
- **Row 1**: White background, brand/logo left, company context, global search center, user dropdown right
- **Row 2**: Olive gradient background, module navigation, dropdown menus, mobile hamburger
- **Files**:
  - `templates/base.html` - Two-row shell structure
  - `static/css/olive-theme.css` - Full styling (~400 lines)
  - `static/js/navigation.js` - Mobile toggle, active state
  - `static/css/mobile.css` - Responsive overrides
- **Features**:
  - Horizontal module navigation on desktop
  - Dropdown menus with "Go to [Module]" + submenus
  - Search with expandable input
  - User avatar + name + dropdown for settings/logout
  - Active state highlighting based on URL
  - Mobile hamburger menu with vertical accordion

### Historical (Deprecated)
- **Single-row top nav**: Earlier implementation using one-row layout - replaced with two-row version
- `templates/includes/sidebar.html` - No longer primary nav
- `templates/includes/topbar.html` - No longer used (absorbed into base.html)

---

## 13. Top Navigation Fix (April 2026)

### Problem
The top navigation was rendering as a broken vertical list instead of a horizontal bar. Dropdown menus were not working correctly - links had `href="#"` with inline styles that could prevent proper navigation.

### Root Causes Identified
1. **Incorrect hrefs**: Dropdown parent links had `href="#"` instead of linking to actual pages
2. **Missing proper dropdown classes**: The template used generic `.dropdown` class instead of `.nav-module-dropdown` which the CSS was designed for
3. **Over-reliance on inline styles**: base.html had many inline styles that conflicted with CSS classes and Bootstrap dropdown behavior
4. **Color contrast issues**: The olive gradient was too light (#6B8E4D) making white text hard to read
5. **Custom JS conflicting with Bootstrap**: navigation.js had click handlers that could interfere with Bootstrap's dropdown handling

### Fixes Applied

**Phase 1: Navigation Behavior**
- Fixed dropdown container: Changed from `<div class="dropdown">` to `<div class="nav-module-dropdown">` to match CSS selectors
- Added "Go to [Module]" link at top of each dropdown for direct navigation to the main module page
- Used Bootstrap's `data-bs-toggle="dropdown"` attribute for proper dropdown behavior
- Removed unnecessary inline styles from nav links that were overriding CSS classes
- Simplified navigation.js - removed custom dropdown click handlers that conflicted with Bootstrap

**Phase 2: Visual Contrast**
- Darkened primary olive color from `#6B8E4D` to `#4a6b3a`
- Darkened gradient from `#3d5630` to `#2d421f` for better contrast
- Improved box-shadow for depth
- Used CSS classes (.brand-link, .nav-search-wrapper, .nav-user-dropdown, etc.) instead of inline styles for consistent styling

**Files Modified:**
- `templates/base.html` - Cleaned up nav structure, removed conflicting inline styles
- `static/css/olive-theme.css` - Updated color palette for better contrast
- `static/js/navigation.js` - Simplified to handle only mobile toggle and active state

### Current State (April 2026)
- ✅ Top navigation renders horizontally on desktop
- ✅ Module dropdowns open via Bootstrap data-bs-toggle
- ✅ Each dropdown has "Go to [Module]" option for direct navigation
- ✅ Search input styled with CSS classes
- ✅ User dropdown styled with CSS classes  
- ✅ Darker olive theme provides better contrast
- ✅ Mobile hamburger menu functional
- ✅ Active state highlighting works

### Still Pending / Known Issues
- Dashboard link uses `dashboard:index` but URL pattern may need verification (currently at `/`)
- Some dropdown submenu items may need proper URLs in context_processor
- Mobile dropdown submenu toggling could be improved
- Test in actual browser to verify all interactions work as expected

---

## 14. Two-Row Enterprise Header — Full Fix (April 2026)

### Root Cause of Rendering Failure
The header structure and CSS were correct on paper, but the rendered UI showed plain vertically-stacked links with no styling. After browser inspection the root causes were:

1. **CSS not applying despite correct DOM/CSS**: The external `olive-theme.css` defined all the header flex rules, but they were not visible in the browser despite the file serving 200 OK. Investigation confirmed that Bootstrap's base styles (loaded first) were not overridden reliably because the custom class names and specificity weren't strong enough in some edge cases.

2. **`overflow: auto` clipping nav dropdowns**: Even after the header rows appeared, the module navigation dropdowns were invisible. The `.app-nav-scroll` container had `overflow-x: auto` which clipped absolutely-positioned dropdown menus that extend below the nav bar. Changed to `overflow: visible`.

3. **`overflow` on `.app-header-nav`**: Same issue — needed `overflow: visible` to allow dropdown menus to extend below the 48px nav bar.

4. **JS dropdown close handler race condition**: The `document.addEventListener('click')` that closed all dropdowns was being triggered on the same event as the trigger click, causing the menu to open and immediately close. Fixed by using a containment check (`dd.contains(e.target)`) so outside-click only closes when the click is genuinely outside all dropdown containers.

### What Was Rewritten

**`templates/base.html`** — Complete structural rewrite:
- **Old**: Used `.app-header-row1` / `.app-header-row2` class names with all CSS in external `olive-theme.css`
- **New**: Renamed to `.app-shell-header` → `.app-header-utility` (Row 1) + `.app-header-nav` (Row 2)
- All layout-critical header CSS **inlined in `<style>` tag** inside `base.html` — eliminates load-order and caching failures
- Dropdown menus use custom `.app-nav-dropdown-menu` (not Bootstrap `.dropdown-menu`) to avoid Bootstrap's `display: none` override
- User menu is a custom `<div class="app-user-menu">` toggled by inline JS — no Bootstrap dependency
- Nav trigger buttons are `<button type="button">` with `data-dropdown` / `data-dropdown-trigger` data attributes for JS targeting
- `overflow: visible` on both `.app-header-nav` and `.app-nav-scroll` so dropdowns are not clipped
- `body.user-authenticated { padding-top: 104px }` instead of body-level padding
- Mobile hamburger toggle with `.mobile-open` class, closes on outside click and resize
- All dropdown JS inlined in `<script>` at bottom of `base.html` — no external JS dependency for header behaviour

**`static/css/olive-theme.css`** — stripped to page-content styles only:
- Removed all header/nav CSS (now inlined in base.html)
- Retained: card styles, button styles, table styles, badge utilities, form control focus states, KPI card styles, modal refinements, utility classes

**`static/js/navigation.js`** — simplified:
- Removed all header dropdown / mobile toggle logic (now inlined)
- Retained only: `Alt+G` keyboard shortcut to focus global search

### Verified Working State (April 2026)
- ✅ Row 1 (white bar): `🌿 Olive ERP` brand + company badge + centered search + user avatar/name + dropdown
- ✅ Row 2 (olive gradient): Dashboard + Finance ▾ + Inventory ▾ + CRM ▾ + HR ▾ + Projects ▾ + Purchasing ▾ + Accounting ▾ + Tax & Compliance ▾
- ✅ Finance dropdown opens: Go to Finance / Dashboard / Invoices / Expenses / Journal / Accounts / Cost Centres / Budgets
- ✅ User dropdown opens: name / email / company / Settings / Logout
- ✅ Active state highlights current module
- ✅ Hover state on all nav items
- ✅ Mobile hamburger collapses nav to vertical menu
- ✅ No raw default-link appearance anywhere

### CSS Architecture (Post-Fix)
```
base.html <style> block        — ALL layout-critical header CSS (inlined)
static/css/olive-theme.css     — Page content styles only (cards, tables, etc.)
static/css/mobile.css          — Calendar, KPI, misc mobile helpers
static/css/accounting.css      — Accounting module-specific styles
```

### Key Class Reference (Current)
| Element | Class |
|---------|-------|
| Fixed header wrapper | `.app-shell-header` |
| Row 1 (white) | `.app-header-utility` |
| Brand link | `.app-brand` |
| Company badge | `.app-company-badge` |
| Search wrapper | `.app-header-search` / `.app-search-wrap` / `.app-search-input` |
| User area | `.app-header-user` / `.app-user-toggle` / `.app-user-menu` |
| Row 2 (olive) | `.app-header-nav` |
| Nav link | `.app-nav-link` |
| Dropdown wrapper | `.app-nav-dropdown` (with `data-dropdown`) |
| Dropdown trigger | `button[data-dropdown-trigger]` |
| Dropdown menu | `.app-nav-dropdown-menu` (toggled via `.open` class) |
| Mobile toggle | `.app-mobile-toggle` |
| Mobile nav scroll | `.app-nav-scroll` (toggled via `.mobile-open` class) |
| Page content | `.app-main-content` |

