from django.shortcuts import render


def products(request):
    return render(request, 'inventory/products.html')


def stock(request):
    return render(request, 'inventory/stock.html')


def warehouses(request):
    return render(request, 'inventory/warehouses.html')


def movements(request):
    return render(request, 'inventory/movements.html')
