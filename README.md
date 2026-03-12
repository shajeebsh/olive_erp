# Olive_ERP

Olive_ERP is a comprehensive, modular Enterprise Resource Planning (ERP) system built with **Python 3.11+**, **Django 4.2 LTS**, and **Wagtail CMS 5.2+**. It leverages Wagtail for content management and internal dashboards while using Django for core business logic.

## Key Features

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
