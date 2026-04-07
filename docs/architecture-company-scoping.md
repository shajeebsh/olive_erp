# Company Scoping Architecture

## Overview
All core business modules in OliveERP scope data by `CompanyProfile` via ForeignKey. This enables multi-tenant design and ensures users only see data for their company.

## Modules with Company Field
| Module | Model | Company Field |
|--------|-------|---------------|
| **finance** | Account, Invoice, JournalEntry, Budget, CostCentre | `company` FK |
| **crm** | Customer, Lead, SalesOrder | `company` FK |
| **hr** | Employee, Department, LeaveRequest, Attendance, PayrollPeriod | `company` FK |
| **projects** | Project | `company` FK |
| **purchasing** | Supplier, PurchaseOrder | `company` FK |
| **inventory** | Product, Warehouse | `company` FK |
| **apps.accounting** | FixedAsset, BankReconciliation, Dividend, CT1Computation | `company` FK |

## Scoping Pattern

### In Views
```python
company = get_user_company(request)
qs = Model.objects.filter(company=company)
```

### In Create Views
```python
if form.is_valid():
    obj = form.save(commit=False)
    obj.company = get_user_company(request)
    obj.save()
    return redirect(...)
```

### In Detail/Edit/Delete Views
```python
company = get_user_company(request)
obj = get_object_or_404(Model, pk=pk, company=company)
```

## Adding Company to a Module
1. Add `company` FK to model: `company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE, related_name='...', null=True, blank=True)`
2. Run `makemigrations` and `migrate`
3. Update views to filter by company in list/detail/edit/delete
4. Update create views to set company on save

## Migrations Created
- `projects/migrations/0002_project_company.py`
- `purchasing/migrations/0003_purchaseorder_company_supplier_company.py`
- `inventory/migrations/0002_product_company.py`
- `inventory/migrations/0003_add_company_to_warehouse.py`

## End-to-End Flows

### Projects
1. **List** (`/projects/active/`) - Shows projects for user's company, searchable by name or customer
2. **Create** - Sets company automatically, redirects to list
3. **Detail** - Shows project with tasks, scoped to company
4. **Edit** - Scoped to company
5. **Delete** - Confirms deletion

### Purchasing
1. **Suppliers List** (`/purchasing/suppliers/`) - Shows suppliers for user's company
2. **Supplier Create** - Sets company automatically
3. **Purchase Orders List** (`/purchasing/orders/`) - Shows POs for user's company, searchable by `po_number` or supplier name
4. **PO Create** - Sets company automatically, newly created POs appear in list
5. **PO Detail/Edit/Delete** - Standard CRUD flow

### Inventory
1. **Products List** (`/inventory/products/`) - Shows products for user's company, searchable by name or SKU
2. **Product Create** - Sets company automatically, newly created products appear in list
3. **Product Detail/Edit/Delete** - Standard CRUD flow
4. **Stock List** (`/inventory/stock/`) - Shows stock levels for products owned by user's company
5. **Warehouses List** (`/inventory/warehouses/`) - Shows warehouses owned by user's company
6. **Warehouse Create** - Sets company automatically
7. **Movements List** (`/inventory/movements/`) - Shows stock movements for products owned by user's company
8. **Movement Create** - Product and warehouse dropdowns filtered to user's company
