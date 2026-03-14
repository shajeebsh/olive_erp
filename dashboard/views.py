from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from company.models import CompanyProfile

@login_required
def index(request):
    company = CompanyProfile.objects.first()
    return render(request, 'dashboard/index.html', {'company': company})

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
