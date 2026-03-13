from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from .models import Invoice, JournalEntry, Account
from .forms import InvoiceForm, JournalEntryForm


@login_required
def invoices(request):
    qs = Invoice.objects.select_related('customer')
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    if query:
        qs = qs.filter(Q(invoice_number__icontains=query) | Q(customer__company_name__icontains=query))
    if status:
        qs = qs.filter(status=status)
    qs = qs.order_by('-issue_date')

    totals = Invoice.objects.aggregate(
        total_paid=Sum('total_amount', filter=Q(status='PAID')),
        total_unpaid=Sum('total_amount', filter=Q(status__in=['SENT', 'DRAFT'])),
        total_overdue=Sum('total_amount', filter=Q(status='OVERDUE')),
    )
    context = {
        'invoices': qs,
        'query': query,
        'status_filter': status,
        'status_choices': Invoice.STATUS_CHOICES,
        'totals': totals,
    }
    return render(request, 'finance/invoices.html', context)


@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('finance:invoices')
    else:
        form = InvoiceForm()
    return render(request, 'finance/invoice_form.html', {'form': form, 'action': 'Create'})


@login_required
def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            return redirect('finance:invoices')
    else:
        form = InvoiceForm(instance=invoice)
    return render(request, 'finance/invoice_form.html', {'form': form, 'action': 'Edit', 'invoice': invoice})


@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        return redirect('finance:invoices')
    return render(request, 'finance/invoice_confirm_delete.html', {'invoice': invoice})


@login_required
def expenses(request):
    # Expenses are journal entries with expense accounts
    expense_accounts = Account.objects.filter(type='EXPENSE').order_by('code')
    context = {'expense_accounts': expense_accounts}
    return render(request, 'finance/expenses.html', context)


@login_required
def journal(request):
    entries = JournalEntry.objects.prefetch_related('lines__account').order_by('-date')
    query = request.GET.get('q', '')
    if query:
        entries = entries.filter(Q(entry_number__icontains=query) | Q(description__icontains=query))
    context = {'entries': entries, 'query': query}
    return render(request, 'finance/journal.html', context)


@login_required
def journal_create(request):
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.created_by = request.user
            entry.save()
            return redirect('finance:journal')
    else:
        form = JournalEntryForm()
    return render(request, 'finance/journal_form.html', {'form': form, 'action': 'Create'})


@login_required
def accounts(request):
    account_list = Account.objects.filter(is_active=True).order_by('code')
    context = {'accounts': account_list}
    return render(request, 'finance/accounts.html', context)
