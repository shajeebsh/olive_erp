from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from company.models import CompanyProfile

from reporting.models import DashboardWidget

@login_required
def index(request):
    company = getattr(request.user, 'company', None)
    if not company:
        company = CompanyProfile.objects.first()
        
    # Feature 12: Dynamic Dashboard Widgets
    widgets = DashboardWidget.objects.filter(is_active=True).order_by('order')
    
    context = {
        'company': company,
        'widgets': widgets,
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def finance_dashboard(request):
    return render(request, 'dashboard/finance_dashboard.html')

@login_required
def inventory_dashboard(request):
    return render(request, 'dashboard/inventory_dashboard.html')

@login_required
def hr_dashboard(request):
    return render(request, 'dashboard/hr_dashboard.html')

@login_required
def crm_dashboard(request):
    return render(request, 'dashboard/crm_dashboard.html')

@login_required
def projects_dashboard(request):
    return render(request, 'dashboard/projects_dashboard.html')

@login_required
def reporting_dashboard(request):
    return render(request, 'dashboard/reporting_dashboard.html')

@login_required
def compliance_dashboard(request):
    return render(request, 'dashboard/compliance_dashboard.html')
