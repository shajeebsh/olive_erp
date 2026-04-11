# Technical Architecture

This document provides a comprehensive overview of OliveERP's technical architecture, design decisions, and scalability strategy.

## System Architecture

Olive ERP follows a **Modular Monolith Architecture** - a single codebase organized into loosely-coupled Django apps, giving you the simplicity of a monolith with the maintainability of modules.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
│    Browser  │  Mobile App  │  API Clients  │ 3rd Party      │
└──────────────┬──────────────────────────────┬───────────────┘
                 │ HTTP/REST                     │
┌──────────────▼──────────────────────────────▼───────────────┐
│                   PRESENTATION LAYER                         │
│  ┌────────────────┐  ┌────────────────┐                     │
│  │ Wagtail CMS    │  │ Django Views   │                     │
│  │ - Public Pages │  │ - CRUD Operations                    │
│  │ - Dashboards   │  │ - Forms/Templates                    │
│  │ - Chart.js     │  │ - Bootstrap 5   │                     │
│  └────────────────┘  └────────────────┘                     │
└──────────────────────────┬──────────────────────────────────┘
                            │
┌──────────────────────────▼──────────────────────────────────┐
│                  APPLICATION LAYER                           │
│  ┌────────┬────────┬────────┬────────┬────────┬────────┐   │
│  │ core   │company │finance │inventory│  crm   │projects│   │
│  ├────────┼────────┼────────┼────────┼────────┼────────┤   │
│  │purchasing│  hr  │dashboard│ home   │        │        │   │
│  └────────┴────────┴────────┴────────┴────────┴────────┘   │
│                         │                                     │
│                   ┌─────▼─────┐                              │
│                   │Services.py│ (Business Logic)             │
│                   └─────┬─────┘                              │
│                         │                                     │
│                   ┌─────▼─────┐                              │
│                   │  Signals  │ (Event-Driven)               │
│                   └─────┬─────┘                              │
└─────────────────────────┼─────────────────────────────��──────┘
                           │
┌─────────────────────────▼────────────────────────────────────┐
│                 BACKGROUND TASKS LAYER                         │
│  ┌─────────────────┐      ┌─────────────────┐               │
│  │   Celery        │─────▶│     Redis       │               │
│  │ - PDF Reports   │      │ - Task Broker   │               │
│  │ - Email Reminders│     │ - Cache         │               │
│  │ - Nightly Jobs  │      │ - Session Store │               │
│  └─────────────────┘      └─────────────────┘               │
└─────────────────────────┼────────────────────────────────────┘
                           │
┌─────────────────────────▼────────────────────────────────────┐
│                      DATA LAYER                               │
│  ┌─────────────────┐      ┌─────────────────┐               │
│  │    MySQL 8.0+   │      │   Redis Cache   │               │
│  │ - ERP Data      │◀────▶│ - Query Cache   │               │
│  │ - Transactions  │      │ - Rate Limiting │               │
│  └─────────────────┘      └─────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### Layer Descriptions

| Layer | Components | Purpose |
|-------|------------|---------|
| Client | Browser, Mobile, API | User interfaces and integrations |
| Presentation | Wagtail CMS, Django Views | Content management and UI rendering |
| Application | Django Apps, Services, Signals | Business logic and module communication |
| Background | Celery, Redis | Async tasks, scheduled jobs |
| Data | MySQL, Redis Cache | Persistent storage and caching |

## Project Structure

```
olive_erp/
├── core/             # Custom User, base mixins, Celery tasks
├── company/          # Singleton profile and currencies
├── finance/          # Accounting and Invoicing
├── inventory/        # Products and Stock
├── crm/              # Customers and Sales
├── purchasing/       # Suppliers and Procurement
├── hr/               # Workforce management
├── projects/         # Project and Task tracking
├── dashboard/        # Wagtail Dashboard pages
├── home/             # Public CMS pages
├── reporting/        # Reporting & BI Layer
├── tax_engine/        # Tax & Compliance
└── wagtailerp/       # Main project configuration
```

## Core Modules

| Module | Responsibility | Key Models |
|--------|----------------|------------|
| core | Foundation | Custom User, Mixins, Celery config |
| company | Global config | CompanyProfile, Currency |
| finance | Double-entry accounting | Account, JournalEntry, Invoice |
| inventory | Stock management | Product, Warehouse, StockLevel |
| crm | Sales & customers | Customer, SalesOrder, Quotation |
| purchasing | Procurement | Supplier, PurchaseOrder, GRN |
| hr | Workforce | Employee, Leave, Attendance |
| projects | Project tracking | Project, Task |
| dashboard | Wagtail dashboards | DashboardPage, ReportPage |
| home | Public CMS | HomePage with StreamField |
| reporting | BI & Analytics | Report definitions, exports |
| tax_engine | Compliance | Country engines, tax calculations |

## Design Patterns

### Service Layer

Each module contains a `services.py` file for business logic, keeping views thin and logic reusable:

```python
# Example: finance/services.py
def process_sales_order(order_id):
    # Validation, pricing, stock reservation
    # Keeps views thin and logic reusable
```

### Signal-Driven Events

Decoupled communication between modules:

```python
# Example: inventory/signals.py
@receiver(post_save, sender=GoodsReceivedNote)
def update_stock(sender, instance, **kwargs):
    # Automatically updates inventory when GRN created
```

### Background Processing

- **Celery + Redis** for async tasks
- PDF generation, email reminders, nightly valuations
- Scheduled compliance deadline notifications

## Security Architecture

### Authentication
- Custom User Model with email as unique identifier
- Support for social authentication (configurable)

### Authorization
- Django Groups (Sales, Inventory, HR, Finance, Admin)
- Row-level access control
- Object-level permissions

### API Security
- Token authentication
- Rate limiting via Django REST Framework
- CORS configuration

### Audit Logging
- `AuditMiddleware` tracking all CUD operations
- Silent logging with user, IP, and payload capture
- Retention policies for compliance

### Permission Middleware
- `PermissionMiddleware` restricting actions based on company-specific `UserRole` assignments
- Granular action-based permissions

## Scalability Strategy

| Layer | Scaling Method | Notes |
|-------|----------------|-------|
| Web | Multiple Django instances + load balancer | Horizontal scaling via Gunicorn workers |
| Workers | Add more Celery workers | Vertical scaling for CPU-bound tasks |
| Cache | Redis cluster | Distributed caching |
| Database | MySQL replication (master-slave) or PostgreSQL | Read replicas for queries |

### Performance Targets

| Operation | Target |
|-----------|--------|
| Report generation | <3 sec (standard), <10 sec (complex) |
| Dashboard load | <2 sec |
| PDF generation | <5 sec |
| Concurrent users | 100+ |
| Transaction records | 1M+ |

### Optimization Techniques

- Redis query caching
- Database query optimization with select_related/prefetch_related
- Celery for expensive background operations
- Index optimization for frequently filtered fields

## Integration Points

- Finance → P&L, Balance Sheet, tax computations
- Inventory → stock valuation reports
- HR → payroll summaries, leave analytics
- CRM → sales pipeline, customer reports
- Projects → budget vs actual, R&D tracking
- Company → company profile for compliance forms

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 4.2 LTS, Wagtail CMS 5.2+, DRF |
| Frontend | Django Templates, Bootstrap 5, HTMX, Chart.js |
| Database | MySQL 8.0+ (or PostgreSQL for production) |
| Task Queue | Celery with Redis |
| Deployment | Docker & Docker Compose |

## Architecture Benefits

- **Modularity** → Easy to maintain and extend
- **Loose Coupling** → Modules communicate via signals/services
- **Performance** → Caching, async tasks, optimized queries
- **Security** → RBAC, custom permissions, audit logging
- **Flexibility** → Wagtail for content, Django for business logic

This architecture provides a production-ready foundation balancing maintainability, scalability, and security for a comprehensive ERP system.

## UI Portability Guide

This guide documents the Olive ERP design system patterns for cross-project portability.

### A. Essential Assets (The "UI Kit")

The following core files are required to implement the Olive ERP design system:

| File | Purpose |
|------|---------|
| `static/css/olive-theme.css` | Styling tokens and component standards |
| `templates/base.html` | Structural layout and inlined critical CSS |
| Google Fonts: Inter (400-700) | Primary typeface |

### B. The "Two-Row" Layout Pattern

The Olive ERP UI follows a two-row hierarchy for consistent navigation:

- **Row 1** (`.app-header-utility`): Contains branding, global search (HTMX), and user identity controls
- **Row 2** (`.app-header-nav`): The themed "Module Ribbon" providing persistent navigation across business areas

```html
<!-- Row 1: Utility Header -->
<header class="app-header-utility">
  <div class="brand">...</div>
  <div class="global-search" hx-get="/search/" ...>...</div>
  <div class="user-identity">...</div>
</header>

<!-- Row 2: Module Navigation -->
<nav class="app-header-nav">
  <!-- Module Ribbon populated from Module Registry -->
</nav>
```

### C. Module Registry Methodology

The navigation system uses a dynamic module registry:

1. **Module Definition**: Each module is defined with:
   - `name`: Display label
   - `icon`: Bootstrap Icons class
   - `url`: Route to module
   - `submenu`: Optional dropdown items

2. **Wagtail Integration**: Use `register_admin_menu_item` hooks to mirror the module navigation pattern in standard Wagtail admin pages.

```python
# Example: Module Registry Structure
MODULES = [
    {"name": "Finance", "icon": "bi-cash-coin", "url": "/finance/", "submenu": [...]},
    {"name": "Inventory", "icon": "bi-box-seam", "url": "/inventory/", "submenu": [...]},
    {"name": "HR", "icon": "bi-people", "url": "/hr/", "submenu": [...]},
]
```

### D. Technical Requirements

The following dependencies are mandatory:

| Dependency | Version | Purpose |
|------------|---------|---------|
| Bootstrap | 5.3+ | Grid system and utility classes |
| HTMX | Latest | Partial page updates and search |
| Bootstrap Icons | Latest | Navigational indicators and UI icons |