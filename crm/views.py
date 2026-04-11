from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count
from .models import Customer, SalesOrder, Lead
from .forms import CustomerForm, SalesOrderForm, LeadForm
from core.utils import get_user_company


@login_required
def customers(request):
    company = get_user_company(request)
    qs = Customer.objects.filter(company=company)
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
            customer = form.save(commit=False)
            customer.company = get_user_company(request)
            if not hasattr(customer, 'user'):
                from django.contrib.auth import get_user_model
                User = get_user_model()
                # Create a user for the customer if needed, or link existing
                # For now just set the current user if no user is assigned
                # In a real ERP this would be handled differently
                customer.user = request.user 
            customer.save()
            return redirect('crm:customers')
    else:
        form = CustomerForm()
    return render(request, 'crm/customer_form.html', {'form': form, 'action': 'Create'})


@login_required
def customer_detail(request, pk):
    company = get_user_company(request)
    customer = get_object_or_404(Customer, pk=pk, company=company)
    sales_orders = SalesOrder.objects.filter(customer=customer).order_by('-order_date')
    context = {
        'customer': customer,
        'sales_orders': sales_orders
    }
    return render(request, 'crm/customer_detail.html', context)


@login_required
def customer_edit(request, pk):
    company = get_user_company(request)
    customer = get_object_or_404(Customer, pk=pk, company=company)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('crm:customers')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'crm/customer_form.html', {'form': form, 'action': 'Edit', 'customer': customer})


@login_required
def customer_delete(request, pk):
    company = get_user_company(request)
    customer = get_object_or_404(Customer, pk=pk, company=company)
    if request.method == 'POST':
        customer.delete()
        return redirect('crm:customers')
    return render(request, 'crm/customer_confirm_delete.html', {'customer': customer})


@login_required
def leads(request):
    company = get_user_company(request)
    qs = Lead.objects.filter(company=company).order_by('-created_at')
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    if query:
        qs = qs.filter(Q(lead_name__icontains=query) | Q(company_name__icontains=query) | Q(email__icontains=query))
    if status_filter:
        qs = qs.filter(status=status_filter)
    context = {
        'leads': qs,
        'query': query,
        'status_filter': status_filter,
    }
    return render(request, 'crm/leads.html', context)


@login_required
def lead_create(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.company = get_user_company(request)
            lead.save()
            return redirect('crm:leads')
    else:
        form = LeadForm()
    return render(request, 'crm/lead_form.html', {'form': form, 'action': 'Create'})


@login_required
def lead_detail(request, pk):
    company = get_user_company(request)
    lead = get_object_or_404(Lead, pk=pk, company=company)
    context = {'lead': lead}
    return render(request, 'crm/lead_detail.html', context)


@login_required
def lead_edit(request, pk):
    company = get_user_company(request)
    lead = get_object_or_404(Lead, pk=pk, company=company)
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect('crm:leads')
    else:
        form = LeadForm(instance=lead)
    return render(request, 'crm/lead_form.html', {'form': form, 'action': 'Edit', 'lead': lead})


@login_required
def lead_delete(request, pk):
    company = get_user_company(request)
    lead = get_object_or_404(Lead, pk=pk, company=company)
    if request.method == 'POST':
        lead.delete()
        return redirect('crm:leads')
    return render(request, 'crm/lead_confirm_delete.html', {'lead': lead})


@login_required
def sales_orders(request):
    company = get_user_company(request)
    qs = SalesOrder.objects.filter(company=company).select_related('customer').order_by('-order_date')
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
            order = form.save(commit=False)
            order.company = get_user_company(request)
            order.save()
            return redirect('crm:sales_orders')
    else:
        form = SalesOrderForm()
    return render(request, 'crm/sales_order_form.html', {'form': form, 'action': 'Create'})


@login_required
def sales_order_detail(request, pk):
    company = get_user_company(request)
    order = get_object_or_404(SalesOrder.objects.prefetch_related('lines__product'), pk=pk, company=company)
    context = {'order': order}
    return render(request, 'crm/sales_order_detail.html', context)


@login_required
def sales_order_edit(request, pk):
    company = get_user_company(request)
    order = get_object_or_404(SalesOrder, pk=pk, company=company)
    if request.method == 'POST':
        form = SalesOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('crm:sales_orders')
    else:
        form = SalesOrderForm(instance=order)
    return render(request, 'crm/sales_order_form.html', {'form': form, 'action': 'Edit', 'order': order})


@login_required
def sales_order_delete(request, pk):
    company = get_user_company(request)
    order = get_object_or_404(SalesOrder, pk=pk, company=company)
    if request.method == 'POST':
        order.delete()
        return redirect('crm:sales_orders')
    return render(request, 'crm/sales_order_confirm_delete.html', {'order': order})


@login_required
def opportunities(request):
    return render(request, 'crm/opportunities.html')


@login_required
def activities(request):
    return render(request, 'crm/activities.html')


# ============================================
# Kanban Pipeline View
# ============================================

@login_required
def lead_kanban(request):
    """HTMX-powered Kanban view for lead pipeline."""
    from django.db.models import Sum
    
    company = get_user_company(request)
    leads = Lead.objects.filter(company=company)
    
    # Group leads by stage
    stages = ['NEW', 'CONTACTED', 'QUALIFIED', 'PROPOSAL', 'WON', 'LOST']
    kanban_board = {}
    
    for stage in stages:
        kanban_board[stage] = leads.filter(status=stage).order_by('-created_at')
    
    # Summary calculations
    total_pipeline = leads.exclude(status='LOST').aggregate(
        total=Sum('estimated_value')
    )['total'] or 0
    
    won_count = leads.filter(status='WON').count()
    lost_count = leads.filter(status='LOST').count()
    converted = won_count + lost_count
    conversion_rate = round((won_count / converted * 100), 1) if converted > 0 else 0
    
    # Top sources
    sources = leads.values('source').annotate(count=models.Count('id')).order_by('-count')[:5]
    
    return render(request, 'crm/lead_kanban.html', {
        'kanban_board': kanban_board,
        'stages': stages,
        'total_pipeline': total_pipeline,
        'conversion_rate': conversion_rate,
        'won_count': won_count,
        'sources': sources,
    })


@login_required
def lead_move_stage(request):
    """HTMX endpoint to move lead to different stage."""
    from django.http import JsonResponse
    
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        new_stage = request.POST.get('stage')
        
        try:
            lead = Lead.objects.get(id=lead_id)
            old_stage = lead.status
            lead.status = new_stage
            lead.save()
            return JsonResponse({'success': True, 'old': old_stage, 'new': new_stage})
        except Lead.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Lead not found'})
    
    return JsonResponse({'success': False, 'error': 'POST required'})
