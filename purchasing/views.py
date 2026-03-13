from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Supplier, PurchaseOrder
from .forms import SupplierForm, PurchaseOrderForm

@login_required
def suppliers(request):
    qs = Supplier.objects.all().order_by('company_name')
    query = request.GET.get('q', '')
    if query:
        qs = qs.filter(Q(company_name__icontains=query) | Q(contact_person__icontains=query))
    return render(request, 'purchasing/suppliers.html', {'suppliers': qs, 'query': query})

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('purchasing:suppliers')
    else:
        form = SupplierForm()
    return render(request, 'purchasing/supplier_form.html', {'form': form, 'action': 'Create'})

@login_required
def purchase_orders(request):
    qs = PurchaseOrder.objects.select_related('supplier').all().order_by('-order_date')
    query = request.GET.get('q', '')
    if query:
        qs = qs.filter(Q(po_number__icontains=query) | Q(supplier__company_name__icontains=query))
    return render(request, 'purchasing/purchase_orders.html', {'purchase_orders': qs, 'query': query})

@login_required
def purchase_order_create(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('purchasing:purchase_orders')
    else:
        form = PurchaseOrderForm()
    return render(request, 'purchasing/purchase_order_form.html', {'form': form, 'action': 'Create'})
