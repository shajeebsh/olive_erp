from django.shortcuts import render

def index(request):
    return render(request, 'dashboard/index.html')

def finance_dashboard(request):
    return render(request, 'dashboard/finance_dashboard.html')

def inventory_dashboard(request):
    return render(request, 'dashboard/inventory_dashboard.html')

def hr_dashboard(request):
    return render(request, 'dashboard/hr_dashboard.html')

def crm_dashboard(request):
    return render(request, 'dashboard/crm_dashboard.html')

def projects_dashboard(request):
    return render(request, 'dashboard/projects_dashboard.html')

def reporting_dashboard(request):
    return render(request, 'dashboard/reporting_dashboard.html')

def compliance_dashboard(request):
    return render(request, 'dashboard/compliance_dashboard.html')
