from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Supplier, PurchaseOrder
from .forms import SupplierForm, PurchaseOrderForm
from core.utils import get_user_company

@login_required
def suppliers(request):
    company = get_user_company(request)
    qs = Supplier.objects.filter(company=company).order_by('company_name')
    query = request.GET.get('q', '')
    if query:
        qs = qs.filter(Q(company_name__icontains=query) | Q(contact_person__icontains=query))
    return render(request, 'purchasing/suppliers.html', {'suppliers': qs, 'query': query})

@login_required
def supplier_create(request):
    company = get_user_company(request)
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.company = company
            supplier.save()
            return redirect('purchasing:suppliers')
    else:
        form = SupplierForm()
    return render(request, 'purchasing/supplier_form.html', {'form': form, 'action': 'Create'})


@login_required
def supplier_detail(request, pk):
    company = get_user_company(request)
    supplier = get_object_or_404(Supplier, pk=pk, company=company)
    orders = PurchaseOrder.objects.filter(supplier=supplier, company=company).order_by('-order_date')
    context = {
        'supplier': supplier,
        'purchase_orders': orders
    }
    return render(request, 'purchasing/supplier_detail.html', context)


@login_required
def supplier_edit(request, pk):
    company = get_user_company(request)
    supplier = get_object_or_404(Supplier, pk=pk, company=company)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('purchasing:suppliers')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'purchasing/supplier_form.html', {'form': form, 'action': 'Edit', 'supplier': supplier})


@login_required
def supplier_delete(request, pk):
    company = get_user_company(request)
    supplier = get_object_or_404(Supplier, pk=pk, company=company)
    if request.method == 'POST':
        supplier.delete()
        return redirect('purchasing:suppliers')
    return render(request, 'purchasing/supplier_confirm_delete.html', {'supplier': supplier})


@login_required
def purchase_orders(request):
    company = get_user_company(request)
    qs = PurchaseOrder.objects.filter(company=company).select_related('supplier').order_by('-order_date')
    query = request.GET.get('q', '')
    if query:
        qs = qs.filter(Q(po_number__icontains=query) | Q(supplier__company_name__icontains=query))
    return render(request, 'purchasing/purchase_orders.html', {'purchase_orders': qs, 'query': query})


@login_required
def purchase_order_detail(request, pk):
    company = get_user_company(request)
    order = get_object_or_404(PurchaseOrder.objects.prefetch_related('lines__product'), pk=pk, company=company)
    context = {'order': order}
    return render(request, 'purchasing/purchase_order_detail.html', context)


@login_required
def purchase_order_edit(request, pk):
    company = get_user_company(request)
    order = get_object_or_404(PurchaseOrder, pk=pk, company=company)
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=order, company=company)
        if form.is_valid():
            form.save()
            return redirect('purchasing:purchase_orders')
    else:
        form = PurchaseOrderForm(instance=order, company=company)
    return render(request, 'purchasing/purchase_order_form.html', {'form': form, 'action': 'Edit', 'order': order})


@login_required
def purchase_order_delete(request, pk):
    company = get_user_company(request)
    order = get_object_or_404(PurchaseOrder, pk=pk, company=company)
    if request.method == 'POST':
        order.delete()
        return redirect('purchasing:purchase_orders')
    return render(request, 'purchasing/purchase_order_confirm_delete.html', {'order': order})


@login_required
def purchase_order_create(request):
    company = get_user_company(request)
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, company=company)
        if form.is_valid():
            order = form.save(commit=False)
            order.company = company
            order.save()
            return redirect('purchasing:purchase_orders')
    else:
        form = PurchaseOrderForm(company=company)
    return render(request, 'purchasing/purchase_order_form.html', {'form': form, 'action': 'Create'})
