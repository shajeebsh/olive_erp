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

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database and secret key details
   ```

3. **Install dependencies**:
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
```

## License

This project is licensed under the MIT License.
