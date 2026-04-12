from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F
from django.db import models
from django.utils import timezone
from datetime import date, timedelta
from company.models import CompanyProfile

from reporting.models import DashboardWidget, Dashboard

from finance.models import Invoice
from crm.models import Customer, Lead, SalesOrder
from hr.models import Employee
from inventory.models import Product, StockLevel
from projects.models import Project, Task


@login_required
def index(request):
    company = getattr(request.user, 'company', None)
    if not company:
        company = CompanyProfile.objects.first()

    # Feature 12: Dynamic Dashboard Widgets — scoped to the company's primary dashboard
    widgets = []
    dashboard = Dashboard.objects.filter(company=company).first() if company else None
    if dashboard:
        widgets = DashboardWidget.objects.filter(
            dashboard=dashboard
        ).order_by('position_y', 'position_x')

    # Cross-module analytics (scoped to company)
    if company:
        # === Finance/Accounting ===
        # Cash Balance: Asset accounts with 'Bank' or 'Cash' in name/code
        from finance.models import Account
        cash_accs = Account.objects.filter(
            company=company,
            account_type='Asset'
        )
        cash_balance = 0
        for acc in cash_accs:
            if 'bank' in acc.name.lower() or 'cash' in acc.name.lower() or 'bank' in acc.code.lower():
                cash_balance += float(acc.get_balance() or 0)
        
        # Receivables: Unpaid invoices (SENT, DRAFT, OVERDUE)
        receivables = Invoice.objects.filter(
            company=company,
            status__in=['SENT', 'DRAFT', 'OVERDUE']
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Payables: Unpaid purchase orders
        from purchasing.models import PurchaseOrder
        payables = PurchaseOrder.objects.filter(
            company=company,
            status__in=['PENDING', 'APPROVED']
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # === Inventory ===
        # Stock Value: Qty * Cost Price
        stock_value_query = StockLevel.objects.filter(
            product__company=company,
            quantity_on_hand__gt=0
        ).select_related('product')
        stock_value = sum(
            float(sl.quantity_on_hand or 0) * float(sl.product.cost_price or 0)
            for sl in stock_value_query
        )
        # Low Stock Alerts: Items <= reorder level
        from django.db.models import F
        low_stock_alerts = StockLevel.objects.filter(
            product__company=company,
            quantity_on_hand__lte=F('reorder_level')
        ).count()
        
        # === CRM ===
        # Pipeline Value: Sum of active lead values
        pipeline_value = Lead.objects.filter(
            company=company,
            status__in=['NEW', 'CONTACTED', 'QUALIFIED', 'PROPOSAL']
        ).aggregate(total=Sum('estimated_value'))['total'] or 0
        
        # Conversion Rate: (Won / (Won + Lost)) * 100
        won_count = Lead.objects.filter(company=company, status='WON').count()
        lost_count = Lead.objects.filter(company=company, status='LOST').count()
        conversion_rate = round((won_count / (won_count + lost_count) * 100), 1) if (won_count + lost_count) > 0 else 0
        
        # === Projects ===
        # Overdue Tasks
        overdue_tasks = Task.objects.filter(
            project__company=company,
            status__in=['TODO', 'IN_PROGRESS'],
            due_date__lt=date.today()
        ).count()
        # Task Completion %
        total_tasks = Task.objects.filter(project__company=company).count()
        completed_tasks = Task.objects.filter(project__company=company, status='DONE').count()
        task_completion_pct = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
        
        # === Compliance ===
        # Filing Deadline Days (placeholder - tax_engine models TBD)
        filing_deadline_days = None
        
        # === Legacy KPIs ===
        total_revenue = Invoice.objects.filter(
            company=company, status='PAID'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        total_products = Product.objects.filter(company=company).count()
        in_stock = StockLevel.objects.filter(
            product__company=company,
            quantity_on_hand__gt=0
        ).values('product').distinct().count()
        employee_count = Employee.objects.filter(company=company).count()
        customer_count = Customer.objects.filter(company=company).count()
        active_leads = Lead.objects.filter(company=company).exclude(status__in=['WON', 'LOST']).count()
        open_orders = SalesOrder.objects.filter(company=company, status='CONFIRMED').count()
        active_projects = Project.objects.filter(company=company, status='IN_PROGRESS').count()
        
        # Chart data: Cash flow (6 months)
        from datetime import date as d
        six_months_ago = d.today() - timedelta(days=180)
        monthly_revenue = list(
            Invoice.objects.filter(
                company=company,
                status='PAID',
                issue_date__gte=six_months_ago
            ).annotate(month=models.functions.TruncMonth('issue_date')
            ).values('month').annotate(total=Sum('total_amount')).order_by('month')
        )
        cash_flow_labels = [m['month'].strftime('%b') if m['month'] else '' for m in monthly_revenue]
        cash_flow_data = [float(m['total'] or 0) for m in monthly_revenue]
        
        # Chart data: Leads by stage
        lead_stage_counts = list(
            Lead.objects.filter(company=company)
            .values('status')
            .annotate(count=Count('id'))
        )
        stage_labels = [l['status'] or 'Unknown' for l in lead_stage_counts]
        stage_data = [l['count'] for l in lead_stage_counts]
        
        # Chart data: Tasks by status
        task_status_counts = list(
            Task.objects.filter(project__company=company)
            .values('status')
            .annotate(count=Count('id'))
        )
        task_labels = [t['status'] or 'Unknown' for t in task_status_counts]
        task_data = [t['count'] for t in task_status_counts]
    else:
        cash_balance = receivables = payables = 0
        stock_value = low_stock_alerts = 0
        pipeline_value = conversion_rate = 0
        overdue_tasks = task_completion_pct = 0
        filing_deadline_days = None
        total_revenue = total_products = in_stock = 0
        employee_count = customer_count = active_leads = 0
        open_orders = active_projects = 0
        cash_flow_labels = cash_flow_data = []
        stage_labels = stage_data = []
        task_labels = task_data = []

    context = {
        'company': company,
        'widgets': widgets,
        'dashboard': dashboard,
        # Executive KPIs
        'cash_balance': cash_balance,
        'receivables': receivables,
        'payables': payables,
        'stock_value': stock_value,
        'low_stock_alerts': low_stock_alerts,
        'pipeline_value': pipeline_value,
        'conversion_rate': conversion_rate,
        'overdue_tasks': overdue_tasks,
        'task_completion_pct': task_completion_pct,
        'filing_deadline_days': filing_deadline_days,
        # Legacy KPIs
        'total_revenue': total_revenue,
        'total_products': total_products,
        'in_stock': in_stock,
        'employee_count': employee_count,
        'customer_count': customer_count,
        'active_leads': active_leads,
        'open_orders': open_orders,
        'active_projects': active_projects,
        # Chart data
        'cash_flow_labels': cash_flow_labels,
        'cash_flow_data': cash_flow_data,
        'stage_labels': stage_labels,
        'stage_data': stage_data,
        'task_labels': task_labels,
        'task_data': task_data,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def finance_dashboard(request):
    company = getattr(request.user, 'company', None)
    if not company:
        company = CompanyProfile.objects.first()

    if company:
        # Invoice stats
        paid_total = Invoice.objects.filter(company=company, status='PAID').aggregate(total=Sum('total_amount'))['total'] or 0
        unpaid_total = Invoice.objects.filter(company=company, status__in=['SENT', 'DRAFT']).aggregate(total=Sum('total_amount'))['total'] or 0
        overdue_total = Invoice.objects.filter(company=company, status='OVERDUE').aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Recent invoices
        recent_invoices = Invoice.objects.filter(company=company).select_related('customer').order_by('-issue_date')[:5]
    else:
        paid_total = unpaid_total = overdue_total = 0
        recent_invoices = []

    context = {
        'company': company,
        'paid_total': paid_total,
        'unpaid_total': unpaid_total,
        'overdue_total': overdue_total,
        'recent_invoices': recent_invoices,
    }
    return render(request, 'dashboard/finance_dashboard.html', context)


@login_required
def inventory_dashboard(request):
    company = getattr(request.user, 'company', None)
    if not company:
        company = CompanyProfile.objects.first()

    if company:
        total_products = Product.objects.filter(company=company).count()
        in_stock_count = StockLevel.objects.filter(
            product__company=company,
            quantity_on_hand__gt=0
        ).values('product').distinct().count()
        
        # Low stock items - quantity <= reorder level
        low_stock_items = StockLevel.objects.filter(
            product__company=company,
            quantity_on_hand__lte=0
        ).select_related('product', 'warehouse')[:5]
        
        # Low stock warnings - approaching reorder level
        low_stock_warning = StockLevel.objects.filter(
            product__company=company,
            quantity_on_hand__gt=0,
            quantity_on_hand__lte=F('reorder_level')
        ).select_related('product', 'warehouse')[:5]

        # Chart data - stock by category
        from inventory.models import Category
        stock_by_category = list(
            Category.objects.filter(
                product__company=company
            ).annotate(
                total_stock=Sum('product__stocklevel__quantity_on_hand')
            ).values('name', 'total_stock')[:6]
        )
        category_labels = [c['name'] or 'Uncategorized' for c in stock_by_category]
        category_data = [float(c['total_stock'] or 0) for c in stock_by_category]
    else:
        total_products = in_stock_count = 0
        low_stock_items = []
        low_stock_warning = []
        category_labels = []
        category_data = []

    context = {
        'company': company,
        'total_products': total_products,
        'in_stock_count': in_stock_count,
        'low_stock_items': low_stock_items,
        'low_stock_warning': low_stock_warning,
        'category_labels': category_labels,
        'category_data': category_data,
    }
    return render(request, 'dashboard/inventory_dashboard.html', context)


@login_required
def hr_dashboard(request):
    company = getattr(request.user, 'company', None)
    if not company:
        company = CompanyProfile.objects.first()

    if company:
        employee_count = Employee.objects.filter(company=company).count()
        employees_with_user = Employee.objects.filter(company=company).exclude(user__isnull=True).count()
        
        # Get departments (distinct count)
        department_count = Employee.objects.filter(company=company).exclude(department__isnull=True).values('department').distinct().count()

        # Chart data - employees by department
        from hr.models import Department
        dept_employees = list(
            Employee.objects.filter(company=company)
            .exclude(department__isnull=True)
            .values('department__name')
            .annotate(count=Count('id'))
        )
        dept_labels = [e['department__name'] or 'No Dept' for e in dept_employees]
        dept_data = [e['count'] for e in dept_employees]
    else:
        employee_count = department_count = 0
        employees_with_user = 0
        dept_labels = []
        dept_data = []

    context = {
        'company': company,
        'employee_count': employee_count,
        'employees_with_user': employees_with_user,
        'department_count': department_count,
        'dept_labels': dept_labels,
        'dept_data': dept_data,
    }
    return render(request, 'dashboard/hr_dashboard.html', context)


@login_required
def crm_dashboard(request):
    company = getattr(request.user, 'company', None)
    if not company:
        company = CompanyProfile.objects.first()

    if company:
        customer_count = Customer.objects.filter(company=company).count()
        active_leads = Lead.objects.filter(company=company).exclude(status__in=['WON', 'LOST']).count()
        open_orders = SalesOrder.objects.filter(company=company, status='CONFIRMED').count()
        
        # Recent customers
        recent_customers = Customer.objects.filter(company=company).order_by('-id')[:5]

        # Chart data - leads by status
        lead_status_counts = list(
            Lead.objects.filter(company=company)
            .values('status')
            .annotate(count=Count('id'))
        )
        status_labels = [l['status'] or 'Unknown' for l in lead_status_counts]
        status_data = [l['count'] for l in lead_status_counts]
    else:
        customer_count = active_leads = open_orders = 0
        recent_customers = []
        status_labels = []
        status_data = []

    context = {
        'company': company,
        'customer_count': customer_count,
        'active_leads': active_leads,
        'open_orders': open_orders,
        'recent_customers': recent_customers,
        'lead_status_labels': status_labels,
        'lead_status_data': status_data,
    }
    return render(request, 'dashboard/crm_dashboard.html', context)


@login_required
def projects_dashboard(request):
    company = getattr(request.user, 'company', None)
    if not company:
        company = CompanyProfile.objects.first()

    if company:
        active_projects = Project.objects.filter(company=company).exclude(status='COMPLETED').count()
        open_tasks = Task.objects.filter(project__company=company, status='TODO').count()
        
        # Overdue tasks
        overdue_tasks = Task.objects.filter(
            project__company=company,
            status__in=['TODO', 'IN_PROGRESS'],
            due_date__lt=date.today()
        ).select_related('project')[:5]
        
        # Recent projects
        recent_projects = Project.objects.filter(company=company).order_by('-start_date')[:5]

        # Chart data - projects by status
        project_status_counts = list(
            Project.objects.filter(company=company)
            .values('status')
            .annotate(count=Count('id'))
        )
        proj_status_labels = [p['status'] or 'Unknown' for p in project_status_counts]
        proj_status_data = [p['count'] for p in project_status_counts]
    else:
        active_projects = open_tasks = 0
        overdue_tasks = []
        recent_projects = []
        proj_status_labels = []
        proj_status_data = []

    context = {
        'company': company,
        'active_projects': active_projects,
        'open_tasks': open_tasks,
        'overdue_tasks': overdue_tasks,
        'recent_projects': recent_projects,
        'proj_status_labels': proj_status_labels,
        'proj_status_data': proj_status_data,
    }
    return render(request, 'dashboard/projects_dashboard.html', context)


@login_required
def reporting_dashboard(request):
    company = getattr(request.user, 'company', None)
    if not company:
        company = CompanyProfile.objects.first()

    # Check for saved reports (if reporting module has report models)
    saved_reports = []
    try:
        from reporting.models import Report
        saved_reports = Report.objects.filter(company=company).order_by('-created_at')[:10] if company else []
    except Exception:
        pass

    context = {
        'company': company,
        'saved_reports': saved_reports,
    }
    return render(request, 'dashboard/reporting_dashboard.html', context)


@login_required
def compliance_dashboard(request):
    company = getattr(request.user, 'company', None)
    if not company:
        company = CompanyProfile.objects.first()

    # Compliance data - placeholder as tax_engine is still in development
    context = {
        'company': company,
        'filings_count': 0,
        'deadlines_upcoming': [],
    }
    return render(request, 'dashboard/compliance_dashboard.html', context)
