from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Q, Sum, F
from .models import Product, Warehouse, StockLevel, StockMovement
from .forms import ProductForm, WarehouseForm, StockMovementForm
from core.utils import get_user_company


@login_required
def products(request):
    company = get_user_company(request)
    qs = Product.objects.filter(company=company).select_related('category')
    query = request.GET.get('q', '')
    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(sku__icontains=query))
    qs = qs.order_by('name')
    context = {'products': qs, 'query': query}
    return render(request, 'inventory/products.html', context)


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related('category'), pk=pk)
    # Get current stock levels
    stock_levels = StockLevel.objects.filter(product=product).select_related('warehouse')
    # Get recent movements
    recent_movements = StockMovement.objects.filter(product=product).select_related('warehouse').order_by('-date')[:10]
    
    context = {
        'product': product,
        'stock_levels': stock_levels,
        'recent_movements': recent_movements
    }
    return render(request, 'inventory/product_detail.html', context)


@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('inventory:products')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form, 'action': 'Create'})


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('inventory:products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form, 'action': 'Edit', 'product': product})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('inventory:products')
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})


@login_required
def stock(request):
    # Overall stock levels across warehouses
    qs = StockLevel.objects.select_related('product', 'warehouse').all()
    query = request.GET.get('q', '')
    if query:
        qs = qs.filter(Q(product__name__icontains=query) | Q(product__sku__icontains=query))
    
    # Simple alert for reaching reorder level
    low_stock = qs.filter(quantity_on_hand__lte=models.F('reorder_level'))
    
    context = {
        'stock_levels': qs, 
        'query': query,
        'low_stock_count': low_stock.count()
    }
    return render(request, 'inventory/stock.html', context)


@login_required
def warehouses(request):
    qs = Warehouse.objects.all()
    context = {'warehouses': qs}
    return render(request, 'inventory/warehouses.html', context)


@login_required
def warehouse_create(request):
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:warehouses')
    else:
        form = WarehouseForm()
    return render(request, 'inventory/warehouse_form.html', {'form': form, 'action': 'Create'})


@login_required
def movements(request):
    qs = StockMovement.objects.select_related('product', 'warehouse', 'created_by').order_by('-date')
    context = {'movements': qs}
    return render(request, 'inventory/movements.html', context)


@login_required
def movement_create(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.created_by = request.user
            movement.save()
            
            # Note: Ideally signal handles stockLevel update, but for MVP demo we can keep it simple.
            # Assuming signals exist based on earlier knowledge of this patterns.
            return redirect('inventory:movements')
    else:
        form = StockMovementForm()
    return render(request, 'inventory/movement_form.html', {'form': form})
