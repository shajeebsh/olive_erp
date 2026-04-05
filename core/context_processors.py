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
        {'name': 'Accounting', 'url': 'accounting:profit_loss', 'icon': 'bi-calculator', 'submenu': [
            {'name': '📊 P&L Statement', 'url': 'accounting:profit_loss'},
            {'name': '⚖️ Balance Sheet', 'url': 'accounting:balance_sheet'},
            {'name': '📑 VAT Summary', 'url': 'accounting:vat_summary'},
            {'name': '🏦 Bank Reconciliation', 'url': 'accounting:bank_reconciliation'},
            {'name': '🚜 Fixed Assets', 'url': 'accounting:asset_list'},
            {'name': '📖 Statutory Registers', 'url': 'accounting:statutory_registers'},
            {'name': '📜 Dividend Register', 'url': 'accounting:dividend_list'},
            {'name': '🤝 Related Party TX', 'url': 'accounting:related_party_list'},
            {'name': '💰 CT1 Computation', 'url': 'accounting:ct1_list'},
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
    base_items = [{'name': '📋 Dashboard', 'url': 'tax_engine:dashboard'}]
    
    country_forms = {
        'IE': [
            {'name': '🇮🇪 VAT3 Return', 'url': 'tax_engine:ie_vat3'},
            {'name': '📄 CRO B1', 'url': 'tax_engine:ie_cro_b1'},
            {'name': '💰 CT1 Corporation Tax', 'url': 'tax_engine:ie_ct1'},
            {'name': '👥 RBO Register', 'url': 'tax_engine:ie_rbo'},
            {'name': '💵 PAYE/PRSI', 'url': 'tax_engine:ie_paye'},
        ],
        'GB': [
            {'name': '🇬🇧 VAT Return (VAT100)', 'url': 'tax_engine:dashboard'},
            # Other features mentioned in tax engine/general knowledge but maybe not fully implemented yet
            {'name': '📊 CT600 Corporate Tax', 'url': 'tax_engine:gb_ct600'},
            {'name': '🏢 Companies House', 'url': 'tax_engine:gb_companies_house'},
            {'name': '💷 PAYE RTI', 'url': 'tax_engine:gb_paye'},
        ],
        'IN': [
            {'name': '🇮🇳 GSTR-3B', 'url': 'tax_engine:in_gstr3b'},
            {'name': '📑 GSTR-1', 'url': 'tax_engine:in_gstr1'},
            {'name': '💰 TDS Returns', 'url': 'tax_engine:in_tds'},
            {'name': '🚚 E-Way Bill', 'url': 'tax_engine:in_eway'},
            {'name': '📱 E-Invoicing', 'url': 'tax_engine:in_einvoice'},
        ],
        'AE': [
            {'name': '🇦🇪 VAT 201', 'url': 'tax_engine:dashboard'},
            {'name': '🧪 Excise Tax', 'url': 'tax_engine:ae_excise'},
            {'name': '🏛️ Corporate Tax', 'url': 'tax_engine:ae_corporate_tax'},
            {'name': '📋 ESR/UBO', 'url': 'tax_engine:ae_esr'},
        ],
    }
    
    base_items.extend(country_forms.get(country_code, []))
    base_items.append({'name': '⏳ Filing History', 'url': 'tax_engine:filing_history'})
    base_items.append({'name': '✅ Approvals', 'url': 'tax_engine:approvals'})
    
    return base_items
