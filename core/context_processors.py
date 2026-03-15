from company.models import CompanyProfile


def navigation_menu(request):
    if not request.user.is_authenticated:
        return {"menu_items": []}

    menu_items = [
        {"name": "Dashboard", "url": "dashboard:index", "icon": "🏠"},
        {"name": "Finance", "url": "dashboard:finance_dashboard", "icon": "💰"},
        {"name": "Inventory", "url": "dashboard:inventory_dashboard", "icon": "📦"},
        {"name": "CRM", "url": "dashboard:crm_dashboard", "icon": "🤝"},
        {"name": "HR", "url": "dashboard:hr_dashboard", "icon": "👥"},
        {"name": "Projects", "url": "dashboard:projects_dashboard", "icon": "📋"},
    ]

    company = getattr(request.user, "company", None)
    if not company:
        company = CompanyProfile.objects.first()

    if company and company.country_code:
        country = company.country_code
        menu_items.append(
            {
                "name": "Compliance",
                "icon": "⚖️",
                "submenu": get_compliance_submenu(country),
            }
        )

    return {"company": company, "menu_items": menu_items}


def get_compliance_submenu(country_code):
    base_items = [{"name": "Dashboard", "url": "compliance:dashboard", "icon": "📋"}]
    country_forms = {
        "IE": [
            {"name": "VAT3 Return", "url": "compliance:vat", "icon": "🇮🇪"},
            {"name": "CRO B1", "url": "compliance:cro_b1", "icon": "📄"},
            {"name": "CT1 Corporation Tax", "url": "compliance:ct1", "icon": "💰"},
            {"name": "RBO Register", "url": "compliance:rbo", "icon": "👥"},
            {"name": "PAYE/PRSI", "url": "compliance:paye", "icon": "💵"},
        ],
        "GB": [
            {"name": "VAT Return", "url": "compliance:dashboard", "icon": "🇬🇧"},
            {"name": "CT600", "url": "compliance:dashboard", "icon": "📊"},
            {"name": "Companies House", "url": "compliance:dashboard", "icon": "🏢"},
            {"name": "PAYE RTI", "url": "compliance:dashboard", "icon": "💷"},
        ],
        "IN": [
            {"name": "GSTR-3B", "url": "compliance:dashboard", "icon": "🇮🇳"},
            {"name": "GSTR-1", "url": "compliance:dashboard", "icon": "📑"},
            {"name": "TDS Returns", "url": "compliance:dashboard", "icon": "💰"},
            {"name": "E-Way Bill", "url": "compliance:dashboard", "icon": "🚚"},
            {"name": "E-Invoicing", "url": "compliance:dashboard", "icon": "📱"},
        ],
        "AE": [
            {"name": "VAT 201", "url": "compliance:dashboard", "icon": "🇦🇪"},
            {"name": "Excise Tax", "url": "compliance:dashboard", "icon": "🧪"},
            {"name": "Corporate Tax", "url": "compliance:dashboard", "icon": "🏛️"},
            {"name": "ESR/UBO", "url": "compliance:dashboard", "icon": "📋"},
        ],
    }

    base_items.extend(country_forms.get(country_code, []))
    base_items.append(
        {"name": "Filing History", "url": "compliance:history", "icon": "⏳"}
    )
    base_items.append(
        {"name": "Approvals", "url": "compliance:approval_workflow", "icon": "✅"}
    )

    return base_items
