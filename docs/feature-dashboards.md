# docs/feature-dashboards.md — Dashboard Module Reference

## Overview

OliveERP has 8 module dashboards, all wired under the `dashboard` app at `dashboard/views.py` and `dashboard/urls.py`. Each dashboard is company-scoped via the `get_user_company` pattern.

---

## Route Map

| URL Path        | View function        | URL name                       | Template                                  |
|-----------------|----------------------|--------------------------------|-------------------------------------------|
| `/`             | `index`              | `dashboard:index`              | `dashboard/index.html`                    |
| `/finance/`     | `finance_dashboard`  | `dashboard:finance_dashboard`  | `dashboard/finance_dashboard.html`        |
| `/inventory/`   | `inventory_dashboard`| `dashboard:inventory_dashboard`| `dashboard/inventory_dashboard.html`      |
| `/hr/`          | `hr_dashboard`       | `dashboard:hr_dashboard`       | `dashboard/hr_dashboard.html`             |
| `/crm/`         | `crm_dashboard`      | `dashboard:crm_dashboard`      | `dashboard/crm_dashboard.html`            |
| `/projects/`    | `projects_dashboard` | `dashboard:projects_dashboard` | `dashboard/projects_dashboard.html`       |
| `/reporting/`   | `reporting_dashboard`| `dashboard:reporting_dashboard`| `dashboard/reporting_dashboard.html`      |
| `/compliance/`  | `compliance_dashboard`| `dashboard:compliance_dashboard`| `dashboard/compliance_dashboard.html`   |

All routes are registered in `wagtailerp/urls.py` under the `dashboard` app prefix.

---

## Data Sources by Dashboard

### Main Dashboard (`/`)
| KPI / Widget         | Model                     | Query                                     | Status     |
|----------------------|---------------------------|-------------------------------------------|------------|
| Revenue              | `finance.Invoice`         | `filter(status='PAID').Sum(total_amount)` | ✅ Live    |
| Products             | `inventory.Product`       | `filter(company).count()`                 | ✅ Live    |
| In Stock             | `inventory.StockLevel`    | `qty > 0` distinct products               | ✅ Live    |
| Employees            | `hr.Employee`             | `filter(company).count()`                 | ✅ Live    |
| Customers            | `crm.Customer`            | `filter(company).count()`                 | ✅ Live    |
| Active Leads         | `crm.Lead`                | `exclude(status__in=['WON','LOST'])`      | ✅ Live    |
| Open Orders          | `crm.SalesOrder`          | `filter(status='CONFIRMED')`              | ✅ Live    |
| Active Projects      | `projects.Project`        | `exclude(status='COMPLETED')`             | ✅ Live    |
| Revenue Trend Chart  | —                         | Placeholder trend, pins final point to `total_revenue` | ⚠️ Trend placeholder |

> **Note:** The revenue trend chart uses `[0,0,0,0,0, total_revenue]` as a placeholder dataset. The final point reflects actual paid revenue. Monthly aggregation should be added in a future pass.

### Finance Dashboard (`/finance/`)
| KPI / Widget         | Model                     | Query                                     | Status     |
|----------------------|---------------------------|-------------------------------------------|------------|
| Paid Revenue         | `finance.Invoice`         | `filter(status='PAID').Sum()`             | ✅ Live    |
| Unpaid               | `finance.Invoice`         | `filter(status__in=['SENT','DRAFT']).Sum()` | ✅ Live  |
| Overdue              | `finance.Invoice`         | `filter(status='OVERDUE').Sum()`          | ✅ Live    |
| Total (Paid+Unpaid)  | Computed in template      | `paid_total + unpaid_total`               | ✅ Live    |
| Invoice Status Chart | Context vars              | Doughnut: paid/unpaid/overdue             | ✅ Live (Chart.js doughnut) |
| Recent Invoices      | `finance.Invoice`         | `order_by('-issue_date')[:5]`             | ✅ Live    |

### Inventory Dashboard (`/inventory/`)
| KPI / Widget         | Model                     | Query                                     | Status     |
|----------------------|---------------------------|-------------------------------------------|------------|
| Total SKUs           | `inventory.Product`       | `filter(company).count()`                 | ✅ Live    |
| In Stock             | `inventory.StockLevel`    | `qty > 0`, distinct by product            | ✅ Live    |
| Out of Stock         | `inventory.StockLevel`    | `qty <= 0`                                | ✅ Live    |
| Low Stock Warnings   | `inventory.StockLevel`    | `0 < qty <= reorder_level`                | ✅ Live    |
| Out-of-Stock Table   | `inventory.StockLevel`    | Top 5 by qty                              | ✅ Live    |
| Low Stock Table      | `inventory.StockLevel`    | Top 5 approaching reorder                 | ✅ Live    |

### HR Dashboard (`/hr/`)
| KPI / Widget         | Model                     | Query                                     | Status     |
|----------------------|---------------------------|-------------------------------------------|------------|
| Total Employees      | `hr.Employee`             | `filter(company).count()`                 | ✅ Live    |
| Employees With Login | `hr.Employee`             | `exclude(user__isnull=True).count()`      | ✅ Live    |
| Departments          | `hr.Employee`             | `distinct department` count               | ✅ Live    |

> **Note:** `Employee` has no `status` field. Do **not** filter by `status='ACTIVE'`.

### CRM Dashboard (`/crm/`)
| KPI / Widget         | Model                     | Query                                     | Status     |
|----------------------|---------------------------|-------------------------------------------|------------|
| Customer Count       | `crm.Customer`            | `filter(company).count()`                 | ✅ Live    |
| Active Leads         | `crm.Lead`                | `exclude(status__in=['WON','LOST'])`      | ✅ Live    |
| Open Orders          | `crm.SalesOrder`          | `filter(status='CONFIRMED')`              | ✅ Live    |
| Recent Customers     | `crm.Customer`            | `order_by('-id')[:5]`                     | ✅ Live    |

> **Note:** `Customer` has no `created_at` field. Use `order_by('-id')` for recency.

### Projects Dashboard (`/projects/`)
| KPI / Widget         | Model                     | Query                                     | Status     |
|----------------------|---------------------------|-------------------------------------------|------------|
| Active Projects      | `projects.Project`        | `exclude(status='COMPLETED')`             | ✅ Live    |
| Open Tasks           | `projects.Task`           | `filter(status='TODO')`                   | ✅ Live    |
| Overdue Tasks        | `projects.Task`           | `status in [TODO,IN_PROGRESS], due < today` | ✅ Live |
| Recent Projects      | `projects.Project`        | `order_by('-start_date')[:5]`             | ✅ Live    |
| Overdue Task Table   | `projects.Task`           | Top 5 overdue                             | ✅ Live    |

### Reporting Dashboard (`/reporting/`)
| KPI / Widget         | Model                     | Query                                     | Status     |
|----------------------|---------------------------|-------------------------------------------|------------|
| Saved Reports        | `reporting.Report`        | `filter(company)[:10]` (try/except)       | ⚠️ Scaffolded |

> Intentionally scaffolded. The Report Builder is a future feature.

### Compliance Dashboard (`/compliance/`)
| KPI / Widget         | Status     | Notes                              |
|----------------------|------------|------------------------------------|
| All KPIs             | ⚠️ Scaffolded | Tax engine under active development. KPIs are zero-valued placeholders. |

---

## Chart Inventory

| Dashboard   | Canvas ID          | Chart Type | Data Source              | Guard           |
|-------------|-------------------|------------|--------------------------|-----------------|
| Main        | `revenueTrendChart` | Line     | `total_revenue` (partial) | `{% if total_revenue > 0 %}` + JS null-check |
| Finance     | `pnlTrendChart`   | Doughnut   | paid/unpaid/overdue totals | `{% if totals > 0 %}` + JS null-check |
| Others      | —                 | —          | No canvas elements        | n/a             |

> **Chart implementation pattern:** All chart `<canvas>` elements are inside a Django `{% if %}` guard. The corresponding `{% block extra_js %}` uses an IIFE with `getElementById` null-check so it never crashes even if the canvas is conditionally absent.

---

## Known Model Gotchas

| Model             | Missing field    | Correct alternative          |
|-------------------|------------------|------------------------------|
| `crm.Customer`    | `created_at`     | `id` (use `order_by('-id')`) |
| `hr.Employee`     | `status`         | No status — count directly   |
| `crm.Lead`        | status `'ACTIVE'`| Exclude `WON`/`LOST` instead |

---

## Empty State Behavior

All dashboards show clean empty states when no data exists:
- KPI values default to `0` via `|default:"0"` in templates
- Tables show "`No X yet`" message in a `text-muted text-center py-3` div
- Charts are hidden (canvas not rendered) when all totals are zero
- Chart sections show a labeled empty-state icon instead of a blank box
