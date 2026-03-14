from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from finance.models import Invoice, Account
from inventory.models import Product
from crm.models import Customer
from django.db.models import Q

class GoToSearchView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        results = []
        if len(query) >= 2:
            # Search Invoices
            invoices = Invoice.objects.filter(
                Q(invoice_number__icontains=query) | Q(customer__company_name__icontains=query)
            )[:5]
            for inv in invoices:
                results.append({
                    'category': 'Invoices',
                    'title': f"Invoice {inv.invoice_number} - {inv.customer.company_name}",
                    'url': f"/finance/invoices/", # Simple link for now
                    'icon': 'fas fa-file-invoice-dollar'
                })

            # Search Products
            products = Product.objects.filter(name__icontains=query)[:5]
            for prod in products:
                results.append({
                    'category': 'Products',
                    'title': prod.name,
                    'url': f"/inventory/",
                    'icon': 'fas fa-box'
                })

            # Search Customers
            customers = Customer.objects.filter(company_name__icontains=query)[:5]
            for cust in customers:
                results.append({
                    'category': 'Customers',
                    'title': cust.company_name,
                    'url': f"/crm/",
                    'icon': 'fas fa-user-friends'
                })

        if request.headers.get('HX-Request'):
            return render(request, 'includes/search_results.html', {'results': results})

        return JsonResponse({'results': results})
