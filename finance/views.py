from django.shortcuts import render

def invoices(request):
    return render(request, 'finance/invoices.html')

def expenses(request):
    return render(request, 'finance/expenses.html')

def journal(request):
    return render(request, 'finance/journal.html')
