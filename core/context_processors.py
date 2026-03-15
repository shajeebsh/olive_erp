from company.models import CompanyProfile

def navigation_menu(request):
    return {
        'company': CompanyProfile.objects.first(),
        'modules': [
            {'name': 'Dashboard', 'url': 'dashboard:index', 'icon': 'bi-house-door'},
            {
                'name': 'Finance',
                'icon': 'bi-cash-coin',
                'submenu': [
                    {'name': 'Dashboard', 'url': 'dashboard:finance_dashboard'},
                    # Invoicing
                    {'name': 'Invoices', 'url': 'finance:invoices'},
                    {'name': 'Recurring Invoices', 'url': 'finance:recurring_invoice_list'},
                    {'name': 'Credit / Debit Notes', 'url': 'finance:note_list'},
                    {'name': 'Invoice Templates', 'url': 'finance:template_list'},
                    # Ledger
                    {'name': 'Chart of Accounts', 'url': 'finance:account_list'},
                    {'name': 'Journal', 'url': 'finance:journal'},
                    {'name': 'Expenses', 'url': 'finance:expenses'},
                    # Planning & Config
                    {'name': 'Cost Centres', 'url': 'finance:costcentre_list'},
                    {'name': 'Budgets', 'url': 'finance:budget_list'},
                    # Pricing
                    {'name': 'Price Lists', 'url': 'finance:pricelist_list'},
                    {'name': 'Discount Rules', 'url': 'finance:discountrule_list'},
                    # Settings
                    {'name': 'System Config', 'url': 'finance:system_config'},
                ]
            },
            {
                'name': 'Inventory',
                'icon': 'bi-box-seam',
                'submenu': [
                    {'name': 'Dashboard', 'url': 'dashboard:inventory_dashboard'},
                    {'name': 'Products', 'url': 'inventory:products'},
                    {'name': 'Stock Levels', 'url': 'inventory:stock'},
                    {'name': 'Warehouses', 'url': 'inventory:warehouses'},
                    {'name': 'Movements', 'url': 'inventory:movements'},
                ]
            },
            {
                'name': 'HR',
                'icon': 'bi-people',
                'submenu': [
                    {'name': 'Dashboard', 'url': 'dashboard:hr_dashboard'},
                    {'name': 'Employees', 'url': 'hr:employees'},
                    {'name': 'Leave', 'url': 'hr:leave'},
                    {'name': 'Attendance', 'url': 'hr:attendance'},
                    {'name': 'Payroll', 'url': 'hr:payroll'},
                ]
            },
            {
                'name': 'CRM',
                'icon': 'bi-heart',
                'submenu': [
                    {'name': 'Dashboard', 'url': 'dashboard:crm_dashboard'},
                    {'name': 'Customers', 'url': 'crm:customers'},
                    {'name': 'Leads', 'url': 'crm:leads'},
                    {'name': 'Opportunities', 'url': 'crm:opportunities'},
                    {'name': 'Activities', 'url': 'crm:activities'},
                ]
            },
            {
                'name': 'Purchasing',
                'icon': 'bi-cart',
                'submenu': [
                    {'name': 'Suppliers', 'url': 'purchasing:suppliers'},
                    {'name': 'Purchase Orders', 'url': 'purchasing:purchase_orders'},
                ]
            },
            {
                'name': 'Projects',
                'icon': 'bi-clipboard-check',
                'submenu': [
                    {'name': 'Dashboard', 'url': 'dashboard:projects_dashboard'},
                    {'name': 'Active Projects', 'url': 'projects:active'},
                    {'name': 'Tasks', 'url': 'projects:tasks'},
                    {'name': 'Timeline', 'url': 'projects:timeline'},
                    {'name': 'Resources', 'url': 'projects:resources'},
                ]
            },
            {
                'name': 'Reporting',
                'icon': 'bi-bar-chart-line',
                'submenu': [
                    {'name': 'Report Builder', 'url': 'reporting:builder'},
                    {'name': 'Saved Reports', 'url': 'reporting:saved'},
                    {'name': 'Scheduled Reports', 'url': 'reporting:scheduled'},
                    {'name': 'Data Sources', 'url': 'reporting:datasources'},
                ]
            },
            {
                'name': 'Compliance',
                'icon': 'bi-shield-check',
                'submenu': [
                    {'name': 'Dashboard', 'url': 'compliance:dashboard'},
                    {'name': 'Approval Workflow', 'url': 'compliance:approval_workflow'},
                    {'name': 'Consolidated Reports', 'url': 'compliance:consolidated_reports'},
                    {'name': 'Compliance Calendar', 'url': 'compliance:calendar'},
                    {'name': 'Filings History', 'url': 'compliance:history'},
                    {
                        'name': 'Country Specific',
                        'submenu': [
                            {'name': 'Ireland', 'url': 'compliance:vat'},
                            {'name': 'United Kingdom', 'url': 'compliance:dashboard'},
                            {'name': 'India', 'url': 'compliance:dashboard'},
                            {'name': 'UAE', 'url': 'compliance:dashboard'},
                        ]
                    },
                ]
            },
            {
                'name': 'Admin',
                'icon': 'bi-gear',
                'submenu': [
                    {'name': 'Company Profile', 'url': 'company:profile'},
                    {'name': 'System Settings', 'url': 'core:system_config'},
                    {'name': 'Audit Trail', 'url': 'core:audit_log'},
                ]
            },
        ]
    }
