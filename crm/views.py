from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Customer, SalesOrder
from .forms import CustomerForm, SalesOrderForm


@login_required
def customers(request):
    qs = Customer.objects.all()
    query = request.GET.get('q', '')
    if query:
        qs = qs.filter(Q(company_name__icontains=query) | Q(contact_person__icontains=query) | Q(email__icontains=query))
    qs = qs.order_by('company_name')
    context = {'customers': qs, 'query': query}
    return render(request, 'crm/customers.html', context)


@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            # For this demo, we auto-assign a user if not present, but in real apps user management is separate.
            customer = form.save(commit=False)
            if not hasattr(customer, 'user'):
                from django.contrib.auth import get_user_model
                User = get_user_model()
                # Create a placeholder user or pick current user (demo choice: pick current)
                customer.user = request.user
            customer.save()
            return redirect('crm:customers')
    else:
        form = CustomerForm()
    return render(request, 'crm/customer_form.html', {'form': form, 'action': 'Create'})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('crm:customers')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'crm/customer_form.html', {'form': form, 'action': 'Edit', 'customer': customer})


@login_required
def sales_orders(request):
    qs = SalesOrder.objects.select_related('customer').all().order_by('-order_date')
    query = request.GET.get('q', '')
    if query:
        qs = qs.filter(Q(order_number__icontains=query) | Q(customer__company_name__icontains=query))
    context = {'orders': qs, 'query': query}
    return render(request, 'crm/sales_orders.html', context)


@login_required
def sales_order_create(request):
    if request.method == 'POST':
        form = SalesOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('crm:sales_orders')
    else:
        form = SalesOrderForm()
    return render(request, 'crm/sales_order_form.html', {'form': form, 'action': 'Create'})


@login_required
def leads(request):
    return render(request, 'crm/leads.html')


@login_required
def opportunities(request):
    return render(request, 'crm/opportunities.html')


@login_required
def activities(request):
    return render(request, 'crm/activities.html')
