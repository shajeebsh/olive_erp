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

def system_config(request):
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group
    User = get_user_model()
    context = {
        'config': {
            'f11_accounting': {'maintain_bill_wise': True, 'interest_calculation': False, 'maintain_cost_centre': True, 'maintain_budget': True},
            'f11_inventory': {'integrate_accounts': True, 'maintain_batch': True, 'multiple_uom': True, 'allow_negative_stock': False},
            'f11_statutory': {'country': 'AE', 'tax_system': 'vat', 'financial_year_start': '01-01'},
            'f12_general': {'date_format': 'dd-mm-yyyy', 'number_format': '1,234.00', 'currency_symbol': 'AED'},
            'f12_voucher': {'skip_date_field': False, 'single_entry_mode': False, 'warn_negative_cash': True}
        },
        'users': User.objects.all(),
        'roles': Group.objects.all()
    }
    return render(request, 'core/system_config.html', context)

def audit_log(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    context = {
        'users': User.objects.all(),
        'audit_logs': [
            {
                'id': 1, 'timestamp': '2025-01-20 10:00:00', 'user': request.user,
                'action': 'UPDATE', 'content_type': 'Invoice', 'object_repr': 'INV-2025-001',
                'ip_address': '192.168.1.5'
            },
            {
                'id': 2, 'timestamp': '2025-01-20 09:30:00', 'user': request.user,
                'action': 'CREATE', 'content_type': 'Customer', 'object_repr': 'Acme Corp',
                'ip_address': '192.168.1.5'
            }
        ]
    }
    return render(request, 'core/audit_log.html', context)
