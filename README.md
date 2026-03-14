# Olive_ERP

Olive_ERP is a comprehensive, modular Enterprise Resource Planning (ERP) system built with **Python 3.11+**, **Django 4.2 LTS**, and **Wagtail CMS 5.2+**. It leverages Wagtail for content management and internal dashboards while using Django for core business logic.

## Key Features

- **Modern UI/UX**: A stunning, intuitive navigation system for all 10+ modules with beautiful dashboards for each module with Chart.js visualizations.
- **Finance & Accounting**: Full double-entry ledger, hierarchical chart of accounts, and multi-currency support.
- **Inventory Management**: Product master, warehouse tracking, stock levels, and automated movements.
- **Sales & CRM**: Customer profiles, Sales Orders, Quotations, and automated invoicing.
- **Purchasing & Procurement**: Supplier management, Purchase Orders, and Goods Received Notes (GRN).
- **Human Resources**: Employee records, department management, leave requests, and attendance tracking.
- **Project Management**: Project tracking with task assignments and status monitoring.
- **CMS Integration**: Wagtail-powered public landing pages and secure internal dashboards with Chart.js visualization.
- **Automation**: Signal-driven workflows for inventory updates and invoice generation.
- **Background Tasks**: Celery/Redis integration for nightly valuations and email reminders.

## Tech Stack

- **Backend**: Django, Wagtail CMS, Django REST Framework.
- **Frontend**: Django Templates, Bootstrap 5, HTMX, Chart.js.
- **Database**: MySQL 8.0+.
- **Task Queue**: Celery with Redis.
- **Deployment**: Docker & Docker Compose.

## Getting Started

### Prerequisites

- Python 3.11+
- MySQL Server
- Redis (for Celery)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd olive_erp
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate on macOS/Linux
   source venv/bin/activate

   # Activate on Windows
   venv\Scripts\activate

   # Deactivate
   deactivate
   
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database and secret key details
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database**:
   ```bash
   python manage.py migrate
   python manage.py create_initial_data
   ```

5. **Create Admin User**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the Server**:
   ```bash
   python manage.py runserver
   ```

### Docker Setup

```bash
docker-compose up --build
```

## Project Structure

```text
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
└── wagtailerp/       # Main project configuration
├── reporting/        # Reporting & BI Layer (NEW)
└── compliance/       # Tax & Compliance (NEW)

## New Modules

### 💰 Universal Core Accounting (Phase 1)

A robust, country-agnostic financial core designed to handle complex double-entry accounting, advanced invoicing, and organizational structure tracking.

**Core Financial Features:**
- **Enhanced Chart of Accounts**: Hierarchical account structures tailored for global accounting principles.
- **Cost Centres & Budgeting**: Departmental expense allocation and variance tracking against planned budgets.
- **Advanced Invoicing**: Price lists, discount rules, recurring invoice schedules via Celery, and multi-line item tracking with auto-computed taxes and discounts.
- **Bill-wise Outstanding Tracking**: Strict tracking of invoices against payments (FIFO or manual allocation).
- **Credit / Debit Notes**: Formal adjustment workflows for customer balance corrections.
- **Invoice Templates**: Customizable layouts for PDF rendering.

**Security & Audit:**
- **Role-Based Access Control**: Granular `PermissionMiddleware` restricting actions based on company-specific `UserRole` assignments.
- **Audit Trail**: Silent `AuditMiddleware` tracking all CUD (Create, Update, Delete) operations across the system with user, IP, and payload tracking.

**Global System Features:**
- **Keyboard Shortcuts**: System-wide navigation via JavaScript global event listeners (e.g., `Alt+G` for Quick Search).
- **System Configurator**: Accounting behavior toggles (equivalent to F11/F12 settings) for enabling modules like Cost Centres, Bill-wise Details, or Budgets per company.

### 📊 Reporting & BI Layer

A comprehensive business intelligence module that provides dynamic reporting, dashboards, and analytics across all ERP modules.

**Key Features:**
- Dynamic drag-drop report builder with saved definitions
- Prebuilt dashboards for Finance, Inventory, HR, CRM, and Projects
- Pivot tables, drill-down analytics, and Chart.js visualizations
- Export to CSV, Excel, and PDF formats
- Celery scheduled reports with email distribution
- Role-based access control using existing Django Groups
- REST API for report management and generation
- Plugin system for custom report types and data sources
- Redis caching for performance optimization

**Performance:** Reports <3s, Dashboards <2s, supports 100+ users and 1M+ records

### 📝 Tax & Compliance (Ireland First)

Comprehensive tax and compliance module starting with Irish regulatory requirements, with extensible framework for other countries.

**Irish Compliance Features:**
- Companies Act 2014 compliance
- CRO Annual Return (Form B1) generation
- Corporation Tax Return (CT1) preparation
- RBO Beneficial Ownership reporting
- VAT Returns (VAT3) automation
- PAYE Modernization payroll reporting
- Financial statements preparation

**Core Capabilities:**
- Automated compliance calendar with Celery reminders
- PDF document generator for filing-ready forms
- Approval workflow integration (CFO → Board → File)
- Complete audit trail for all compliance actions
- Multi-country framework for future expansion (UK, EU)

## System Architecture

Olive ERP follows a **Modular Monolith Architecture** - a single codebase organized into loosely-coupled Django apps, giving you the simplicity of a monolith with the maintainability of modules.
- Follow modular monolith pattern (existing olive_erp structure)
- Service layer in services.py, signals for events
- REST API using DRF
- Use existing Django Groups for permissions

Integration Points:
- Finance → P&L, Balance Sheet, tax computations
- Inventory → stock valuation reports
- HR → payroll summaries, leave analytics
- CRM → sales pipeline, customer reports
- Projects → budget vs actual, R&D tracking
- Company → company profile for compliance forms

Performance SLAs:
- Report generation: <3 sec (standard), <10 sec (complex)
- Dashboard load: <2 sec
- PDF generation: <5 sec
- Support 100+ concurrent users
- Handle 1M+ transaction records

Security:
- Authentication via Custom User Model
- Authorization via Django Groups (Sales, Finance, HR, etc.)
- Object-level permissions
- Audit logging for compliance actions

Testing:
- Unit tests for services
- Integration tests with existing modules
- Performance/load tests
- Regulatory validation (test against sample filings)

===========================================================
OUTPUT REQUIREMENTS
===========================================================

For each deliverable, provide:
1. File path (e.g., reporting/models.py)
2. Complete production-ready code
3. Key design decisions explained
4. Follow PEP 8, include docstrings
5. Git commands for each commit
6. Documentation content for each file

Generate complete implementation for both modules with all git commands and documentation updates.
## System Architecture

Olive ERP follows a **Modular Monolith Architecture** - a single codebase organized into loosely-coupled Django apps, giving you the simplicity of a monolith with the maintainability of modules.

### 📊 High-Level Architecture

```text
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
└─────────────────────────┼────────────────────────────────────┘
                           │
┌─────────────────────────▼────────────────────────────────────┐
│                 BACKGROUND TASKS LAYER                        │
│  ┌─────────────────┐      ┌─────────────────┐               │
│  │   Celery        │─────▶│     Redis       │               │
│  │ - PDF Reports   │      │ - Task Broker   │               │
│  │ - Email Reminders│     │ - Cache         │               │
│  │ - Nightly Jobs  │      │ - Session Store │               │
│  └─────────────────┘      └─────────────────┘               │
└─────────────────────────┬────────────────────────────────────┘
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

### 🧩 Core Modules

| Module        | Responsibility          | Key Models                          |
|---------------|-------------------------|-------------------------------------|
| core          | Foundation              | Custom User, Mixins, Celery config |
| company       | Global config           | CompanyProfile, Currency           |
| finance       | Double-entry accounting | Account, JournalEntry, Invoice     |
| inventory     | Stock management        | Product, Warehouse, StockLevel      |
| crm           | Sales & customers       | Customer, SalesOrder, Quotation     |
| purchasing    | Procurement             | Supplier, PurchaseOrder, GRN       |
| hr            | Workforce               | Employee, Leave, Attendance        |
| projects      | Project tracking        | Project, Task                      |
| dashboard     | Wagtail dashboards      | DashboardPage, ReportPage          |
| home          | Public CMS              | HomePage with StreamField          |

### 🔄 Key Design Patterns

#### Service Layer

```python
# Each module has services.py for business logic
def process_sales_order(order_id):
    # Validation, pricing, stock reservation
    # Keeps views thin and logic reusable
```

#### Signal-Driven Events

```python
# Decoupled communication between modules
@receiver(post_save, sender=GoodsReceivedNote)
def update_stock(sender, instance, **kwargs):
    # Automatically updates inventory when GRN created
```

#### Background Processing

- **Celery + Redis** for async tasks
- PDF generation, email reminders, nightly valuations

### 🔐 Security Architecture

- **Authentication**: Custom User Model (email as unique identifier)
- **Authorization**: Django Groups (Sales, Inventory, HR, Finance, Admin)
- **Permissions**: Row-level access, object permissions
- **API Security**: Token authentication, rate limiting

### 🚀 Scalability Strategy

| Layer         | Scaling Method                          |
|--------------|-----------------------------------------|
| Web          | Multiple Django instances + load balancer |
| Workers      | Add more Celery workers                |
| Cache        | Redis cluster                          |
| Database     | MySQL replication (master-slave)       |

### ✅ Architecture Benefits

- **Modularity** → Easy to maintain and extend
- **Loose Coupling** → Modules communicate via signals/services
- **Performance** → Caching, async tasks, optimized queries
- **Security** → RBAC, custom permissions
- **Flexibility** → Wagtail for content, Django for business logic

This architecture provides a production-ready foundation balancing maintainability, scalability, and security for a comprehensive ERP system.
```

## License

This project is licensed under the MIT License.
