# OliveERP

OliveERP is a comprehensive, modular Enterprise Resource Planning (ERP) system built with **Python 3.11+**, **Django 4.2 LTS**, and **Wagtail CMS 5.2+**. It leverages Wagtail for content management and internal dashboards while using Django for core business logic.

## Key Features

- **Modern UI/UX**: Intuitive navigation system for all modules with beautiful dashboards and Chart.js visualizations
- **Finance & Accounting**: Full double-entry ledger, hierarchical chart of accounts, and multi-currency support
- **Inventory Management**: Product master, warehouse tracking, stock levels, and automated movements
- **Sales & CRM**: Customer profiles, Sales Orders, Quotations, and automated invoicing
- **Purchasing & Procurement**: Supplier management, Purchase Orders, and Goods Received Notes (GRN)
- **Human Resources**: Employee records, department management, leave requests, and attendance tracking
- **Project Management**: Project tracking with task assignments and status monitoring
- **Tax & Compliance**: Pluggable country framework with full implementations for Ireland, UK, India, and UAE
- **Reporting & BI**: Dynamic report builder with prebuilt dashboards and export capabilities
- **Automation**: Signal-driven workflows and Celery/Redis for background tasks

## Module Breakdown

| Module | Description | Key Models |
|--------|-------------|-----------|
| Finance | Double-entry accounting | Account, JournalEntry, Invoice |
| Inventory | Stock management | Product, Warehouse, StockLevel |
| CRM | Sales & customers | Customer, SalesOrder, Quotation |
| Purchasing | Procurement | Supplier, PurchaseOrder, GRN |
| HR | Workforce management | Employee, Leave, Attendance |
| Projects | Project tracking | Project, Task |
| Reporting | BI & analytics | Report definitions, exports |
| Tax Engine | Compliance | Country engines, tax returns |

## Tech Stack

- **Backend**: Django 4.2 LTS, Wagtail CMS 5.2+, Django REST Framework
- **Frontend**: Django Templates, Bootstrap 5, HTMX, Chart.js
- **Database**: MySQL 8.0+ (PostgreSQL recommended for production)
- **Task Queue**: Celery with Redis
- **Deployment**: Docker & Docker Compose

## Documentation

- [🚀 Quick Start & Installation](docs/INSTALL.md)
- [🏗️ Technical Architecture](docs/ARCHITECTURE.md)
- [📝 Detailed Feature Docs](docs/ai_context.md)

## License

This project is licensed under the MIT License.