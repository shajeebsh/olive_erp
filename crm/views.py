from django.shortcuts import render


def customers(request):
    return render(request, 'crm/customers.html')


def leads(request):
    return render(request, 'crm/leads.html')


def opportunities(request):
    return render(request, 'crm/opportunities.html')


def activities(request):
    return render(request, 'crm/activities.html')
