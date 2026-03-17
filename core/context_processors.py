from company.models import CompanyProfile

def navigation_menu(request):
    if not request.user.is_authenticated:
        return {'modules': []}
    
    company = getattr(request.user, 'company', None)
    if not company:
        company = CompanyProfile.objects.first()
    
    modules = [
        {'name': 'Dashboard', 'url': 'dashboard:index', 'icon': 'bi-house-door'},
        {'name': 'Finance', 'url': 'dashboard:finance_dashboard', 'icon': 'bi-cash-coin', 'submenu': [
            {'name': '📊 Dashboard', 'url': 'dashboard:finance_dashboard'},
            {'name': '🧾 Invoices', 'url': 'finance:invoices'},
            {'name': '💸 Expenses', 'url': 'finance:expenses'},
            {'name': '📔 Journal', 'url': 'finance:journal'},
            {'name': '🏦 Accounts', 'url': 'finance:account_list'},
            {'name': '📍 Cost Centres', 'url': 'finance:costcentre_list'},
            {'name': '💰 Budgets', 'url': 'finance:budget_list'},
        ]},
        {'name': 'Inventory', 'url': 'dashboard:inventory_dashboard', 'icon': 'bi-box-seam', 'submenu': [
            {'name': '📊 Dashboard', 'url': 'dashboard:inventory_dashboard'},
            {'name': '📦 Products', 'url': 'inventory:products'},
            {'name': '📉 Stock', 'url': 'inventory:stock'},
            {'name': '🏗️ Warehouses', 'url': 'inventory:warehouses'},
            {'name': '🔄 Movements', 'url': 'inventory:movements'},
        ]},
        {'name': 'CRM', 'url': 'dashboard:crm_dashboard', 'icon': 'bi-heart', 'submenu': [
            {'name': '📊 Dashboard', 'url': 'dashboard:crm_dashboard'},
            {'name': '👥 Customers', 'url': 'crm:customers'},
            {'name': '🛒 Sales Orders', 'url': 'crm:sales_orders'},
            {'name': '🎯 Leads', 'url': 'crm:leads'},
            {'name': '💎 Opportunities', 'url': 'crm:opportunities'},
            {'name': '📅 Activities', 'url': 'crm:activities'},
        ]},
        {'name': 'HR', 'url': 'dashboard:hr_dashboard', 'icon': 'bi-people', 'submenu': [
            {'name': '📊 Dashboard', 'url': 'dashboard:hr_dashboard'},
            {'name': '👤 Employees', 'url': 'hr:employees'},
            {'name': '🏖️ Leave', 'url': 'hr:leave'},
            {'name': '🕒 Attendance', 'url': 'hr:attendance'},
            {'name': '💸 Payroll', 'url': 'hr:payroll'},
        ]},
        {'name': 'Projects', 'url': 'dashboard:projects_dashboard', 'icon': 'bi-clipboard-check', 'submenu': [
            {'name': '📊 Dashboard', 'url': 'dashboard:projects_dashboard'},
            {'name': '🏗️ Active Projects', 'url': 'projects:active'},
            {'name': '📋 Tasks', 'url': 'projects:tasks'},
            {'name': '📈 Timeline', 'url': 'projects:timeline'},
            {'name': '👥 Resources', 'url': 'projects:resources'},
        ]},
        {'name': 'Purchasing', 'url': 'purchasing:purchase_orders', 'icon': 'bi-cart', 'submenu': [
            {'name': '🤝 Suppliers', 'url': 'purchasing:suppliers'},
            {'name': '🛒 Purchase Orders', 'url': 'purchasing:purchase_orders'},
        ]},
    ]
    
    if company and company.country_code:
        country = company.country_code
        modules.append({
            'name': 'Compliance',
            'icon': 'bi-shield-check',
            'submenu': get_compliance_submenu(country)
        })
    
    return {'modules': modules, 'company': company}

def get_compliance_submenu(country_code):
    base_items = [{'name': '📋 Dashboard', 'url': 'compliance:dashboard'}]
    
    country_forms = {
        'IE': [
            {'name': '🇮🇪 VAT3 Return', 'url': 'compliance:vat'},
            {'name': '📄 CRO B1', 'url': 'compliance:cro_b1'},
            {'name': '💰 CT1 Corporation Tax', 'url': 'compliance:ct1'},
            {'name': '👥 RBO Register', 'url': 'compliance:rbo'},
            {'name': '💵 PAYE/PRSI', 'url': 'compliance:paye'},
        ],
        'GB': [
            {'name': '🇬🇧 VAT Return', 'url': 'compliance:vat'},
            {'name': '📊 CT600', 'url': 'compliance:vat'}, # Placeholder link
            {'name': '🏢 Companies House', 'url': 'compliance:vat'}, # Placeholder
            {'name': '💷 PAYE RTI', 'url': 'compliance:vat'}, # Placeholder
        ],
        'IN': [
            {'name': '🇮🇳 GSTR-3B', 'url': 'compliance:vat'},
            {'name': '📑 GSTR-1', 'url': 'compliance:vat'}, # Placeholder
            {'name': '💰 TDS Returns', 'url': 'compliance:vat'}, # Placeholder
            {'name': '🚚 E-Way Bill', 'url': 'compliance:vat'}, # Placeholder
            {'name': '📱 E-Invoicing', 'url': 'compliance:vat'}, # Placeholder
        ],
        'AE': [
            {'name': '🇦🇪 VAT 201', 'url': 'compliance:vat'},
            {'name': '🧪 Excise Tax', 'url': 'compliance:vat'}, # Match test assertion
            {'name': '🏛️ Corporate Tax', 'url': 'compliance:vat'},
            {'name': '📋 ESR/UBO', 'url': 'compliance:vat'},
        ],
    }
    
    base_items.extend(country_forms.get(country_code, []))
    base_items.append({'name': '📅 Calendar', 'url': 'compliance:calendar'})
    base_items.append({'name': '⏳ Filing History', 'url': 'compliance:history'})
    base_items.append({'name': '✅ Approvals', 'url': 'compliance:approval_workflow'})
    
    return base_items
