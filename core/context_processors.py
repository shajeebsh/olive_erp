def navigation_menu(request):
    return {
        'modules': [
            {'name': 'Dashboard', 'url': 'dashboard:index', 'icon': 'bi-house-door'},
            {
                'name': 'Finance',
                'icon': 'bi-cash-coin',
                'submenu': [
                    {'name': 'Dashboard', 'url': 'dashboard:finance_dashboard'},
                    {'name': 'Invoices', 'url': 'finance:invoices'},
                    {'name': 'Expenses', 'url': 'finance:expenses'},
                    {'name': 'Journal', 'url': 'finance:journal'},
                    {'name': 'Reports', 'url': 'reporting:index'},
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
                    {'name': 'Dashboard', 'url': 'dashboard:compliance_dashboard'},
                    {
                        'name': 'Ireland',
                        'submenu': [
                            {'name': 'CRO B1', 'url': 'compliance:cro_b1'},
                            {'name': 'CT1 Return', 'url': 'compliance:ct1'},
                            {'name': 'VAT Returns', 'url': 'compliance:vat'},
                            {'name': 'RBO', 'url': 'compliance:rbo'},
                            {'name': 'PAYE', 'url': 'compliance:paye'},
                        ]
                    },
                    {'name': 'Calendar', 'url': 'compliance:calendar'},
                    {'name': 'Filings History', 'url': 'compliance:history'},
                ]
            },
            {
                'name': 'Admin',
                'icon': 'bi-gear',
                'submenu': [
                    {'name': 'Company Profile', 'url': 'company:profile'},
                    {'name': 'User Management', 'url': 'company:profile'},
                    {'name': 'System Settings', 'url': 'company:profile'},
                    {'name': 'Security Logs', 'url': 'company:profile'},
                ]
            },
        ]
    }
