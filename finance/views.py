from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum
from .forms import (
    InvoiceForm, JournalEntryForm, AccountForm, PriceListForm, 
    DiscountRuleForm, RecurringInvoiceForm, CreditDebitNoteForm
)
from .models import (
    Invoice, JournalEntry, Account, JournalEntryLine, CostCentre, Budget,
    PriceList, DiscountRule, RecurringInvoice, CreditDebitNote, 
    InvoiceTemplate, SystemConfig
)
from core.utils import get_user_company


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'finance/invoices.html'
    context_object_name = 'invoices'
    
    def get_queryset(self):
        company = get_user_company(self.request)
        qs = Invoice.objects.filter(company=company).select_related('customer')
        query = self.request.GET.get('q', '')
        status = self.request.GET.get('status', '')
        if query:
            qs = qs.filter(Q(invoice_number__icontains=query) | Q(customer__company_name__icontains=query))
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-issue_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = get_user_company(self.request)
        context['query'] = self.request.GET.get('q', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['status_choices'] = Invoice.STATUS_CHOICES
        context['totals'] = Invoice.objects.filter(company=company).aggregate(
            total_paid=Sum('total_amount', filter=Q(status='PAID')),
            total_unpaid=Sum('total_amount', filter=Q(status__in=['SENT', 'DRAFT'])),
            total_overdue=Sum('total_amount', filter=Q(status='OVERDUE')),
        )
        return context

class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'finance/invoice_form.html'
    success_url = reverse_lazy('finance:invoices')
    extra_context = {'action': 'Create'}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = get_user_company(self.request)
        return kwargs

    def form_valid(self, form):
        form.instance.company = get_user_company(self.request)
        messages.success(self.request, 'Invoice created successfully')
        return super().form_valid(form)

class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'finance/invoice_form.html'
    success_url = reverse_lazy('finance:invoices')
    extra_context = {'action': 'Edit'}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = get_user_company(self.request)
        return kwargs

    def get_queryset(self):
        return Invoice.objects.filter(company=get_user_company(self.request))

    def form_valid(self, form):
        messages.success(self.request, 'Invoice updated successfully')
        return super().form_valid(form)


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name = 'finance/invoice_confirm_delete.html'
    success_url = reverse_lazy('finance:invoices')

    def get_queryset(self):
        return Invoice.objects.filter(company=get_user_company(self.request))

class JournalEntryListView(LoginRequiredMixin, ListView):
    model = JournalEntry
    template_name = 'finance/journal.html'
    context_object_name = 'entries'
    
    def get_queryset(self):
        company = get_user_company(self.request)
        entries = JournalEntry.objects.filter(
            lines__account__company=company
        ).prefetch_related('lines__account').distinct().order_by('-date')
        query = self.request.GET.get('q', '')
        if query:
            entries = entries.filter(Q(entry_number__icontains=query) | Q(description__icontains=query))
        return entries

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class JournalEntryCreateView(LoginRequiredMixin, CreateView):
    model = JournalEntry
    form_class = JournalEntryForm
    template_name = 'finance/journal_form.html'
    success_url = reverse_lazy('finance:journal')
    extra_context = {'action': 'Create'}
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.company = get_user_company(self.request)
        messages.success(self.request, 'Journal Entry created successfully')
        return super().form_valid(form)

class ExpenseListView(LoginRequiredMixin, ListView):
    model = Account
    template_name = 'finance/expenses.html'
    context_object_name = 'expense_accounts'
    
    def get_queryset(self):
        company = get_user_company(self.request)
        return Account.objects.filter(company=company, account_type='Expense').order_by('code')

class AccountListView(LoginRequiredMixin, ListView):
    model = Account
    template_name = 'finance/account_list.html'
    context_object_name = 'accounts'
    paginate_by = 50
    
    def get_queryset(self):
        if hasattr(self.request.user, 'company') and get_user_company(self.request):
            return Account.objects.filter(
                company=get_user_company(self.request)
            ).select_related('parent').order_by('code')
        return Account.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'company') and get_user_company(self.request):
            # Group accounts by type for tree view
            accounts_by_type = {}
            for account_type, _ in Account.ACCOUNT_TYPES:
                accounts_by_type[account_type] = Account.objects.filter(
                    company=get_user_company(self.request),
                    account_type=account_type
                ).select_related('parent')
            context['accounts_by_type'] = accounts_by_type
        return context

class AccountCreateView(LoginRequiredMixin, CreateView):
    model = Account
    form_class = AccountForm
    template_name = 'finance/account_form.html'
    success_url = reverse_lazy('finance:account_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = get_user_company(self.request)
        return kwargs
    
    def form_valid(self, form):
        form.instance.company = get_user_company(self.request)
        messages.success(self.request, 'Account created successfully')
        return super().form_valid(form)

class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = Account
    form_class = AccountForm
    template_name = 'finance/account_form.html'
    success_url = reverse_lazy('finance:account_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = get_user_company(self.request)
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Account updated successfully')
        return super().form_valid(form)

class AccountDetailView(LoginRequiredMixin, DetailView):
    model = Account
    template_name = 'finance/account_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get recent transactions
        context['recent_transactions'] = JournalEntryLine.objects.filter(
            account=self.object
        ).select_related('journal_entry').order_by('-journal_entry__date')[:20]
        
        # Get current balance
        context['current_balance'] = self.object.get_balance()
        return context


class CostCentreListView(LoginRequiredMixin, ListView):
    model = CostCentre
    template_name = 'finance/costcentre_list.html'
    context_object_name = 'cost_centres'
    
    def get_queryset(self):
        return CostCentre.objects.filter(company=get_user_company(self.request))


class CostCentreCreateView(LoginRequiredMixin, CreateView):
    model = CostCentre
    fields = ['code', 'name', 'parent', 'description', 'is_active']
    template_name = 'finance/costcentre_form.html'
    success_url = reverse_lazy('finance:costcentre_list')
    
    def form_valid(self, form):
        form.instance.company = get_user_company(self.request)
        messages.success(self.request, 'Cost Centre created successfully')
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        company = get_user_company(self.request)
        form.fields['parent'].queryset = CostCentre.objects.filter(company=company)
        return form


class CostCentreUpdateView(LoginRequiredMixin, UpdateView):
    model = CostCentre
    fields = ['code', 'name', 'parent', 'description', 'is_active']
    template_name = 'finance/costcentre_form.html'
    success_url = reverse_lazy('finance:costcentre_list')
    
    def get_queryset(self):
        company = get_user_company(self.request)
        return CostCentre.objects.filter(company=company)
    
    def form_valid(self, form):
        messages.success(self.request, 'Cost Centre updated successfully')
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        company = get_user_company(self.request)
        form.fields['parent'].queryset = CostCentre.objects.filter(company=company).exclude(pk=self.object.pk)
        return form


class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'finance/budget_list.html'
    context_object_name = 'budgets'
    
    def get_queryset(self):
        return Budget.objects.filter(company=get_user_company(self.request))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Update actuals before display
        for budget in context['budgets']:
            budget.update_actual()
        return context


class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    fields = ['name', 'financial_year', 'account', 'cost_centre', 
              'period', 'budget_amount', 'notes']
    template_name = 'finance/budget_form.html'
    success_url = reverse_lazy('finance:budget_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['account'].queryset = Account.objects.filter(
            company=get_user_company(self.request),
            account_type__in=['Income', 'Expense']
        )
        form.fields['cost_centre'].queryset = CostCentre.objects.filter(
            company=get_user_company(self.request)
        )
        return form
    
    def form_valid(self, form):
        form.instance.company = get_user_company(self.request)
        messages.success(self.request, 'Budget created successfully')
        return super().form_valid(form)


class PriceListView(LoginRequiredMixin, ListView):
    model = PriceList
    template_name = 'finance/pricelist_list.html'
    context_object_name = 'price_lists'

    def get_queryset(self):
        return PriceList.objects.filter(company=get_user_company(self.request))


class PriceListCreateView(LoginRequiredMixin, CreateView):
    model = PriceList
    form_class = PriceListForm
    template_name = 'finance/pricelist_form.html'
    success_url = reverse_lazy('finance:pricelist_list')

    def form_valid(self, form):
        form.instance.company = get_user_company(self.request)
        return super().form_valid(form)


class DiscountRuleListView(LoginRequiredMixin, ListView):
    model = DiscountRule
    template_name = 'finance/discountrule_list.html'
    context_object_name = 'rules'

    def get_queryset(self):
        return DiscountRule.objects.filter(company=get_user_company(self.request))


class DiscountRuleCreateView(LoginRequiredMixin, CreateView):
    model = DiscountRule
    form_class = DiscountRuleForm
    template_name = 'finance/discountrule_form.html'
    success_url = reverse_lazy('finance:discountrule_list')

    def form_valid(self, form):
        form.instance.company = get_user_company(self.request)
        return super().form_valid(form)


class RecurringInvoiceListView(LoginRequiredMixin, ListView):
    model = RecurringInvoice
    template_name = 'finance/recurring_invoice_list.html'
    context_object_name = 'recurring_invoices'

    def get_queryset(self):
        return RecurringInvoice.objects.filter(company=get_user_company(self.request))


class RecurringInvoiceCreateView(LoginRequiredMixin, CreateView):
    model = RecurringInvoice
    form_class = RecurringInvoiceForm
    template_name = 'finance/recurring_invoice_form.html'
    success_url = reverse_lazy('finance:recurring_invoice_list')

    def form_valid(self, form):
        form.instance.company = get_user_company(self.request)
        # Dummy values for mandatory fields not in form
        form.instance.subtotal = 0
        form.instance.tax_amount = 0
        form.instance.total_amount = 0
        form.instance.items = {} 
        return super().form_valid(form)


class CreditDebitNoteListView(LoginRequiredMixin, ListView):
    model = CreditDebitNote
    template_name = 'finance/note_list.html'
    context_object_name = 'notes'

    def get_queryset(self):
        return CreditDebitNote.objects.filter(company=get_user_company(self.request))


class CreditDebitNoteCreateView(LoginRequiredMixin, CreateView):
    model = CreditDebitNote
    form_class = CreditDebitNoteForm
    template_name = 'finance/note_form.html'
    success_url = reverse_lazy('finance:note_list')

    def form_valid(self, form):
        form.instance.company = get_user_company(self.request)
        return super().form_valid(form)


class InvoiceTemplateListView(LoginRequiredMixin, ListView):
    model = InvoiceTemplate
    template_name = 'finance/template_list.html'
    context_object_name = 'templates'

    def get_queryset(self):
        return InvoiceTemplate.objects.filter(company=get_user_company(self.request))


class SystemConfigUpdateView(LoginRequiredMixin, UpdateView):
    model = SystemConfig
    fields = ['base_currency', 'fiscal_year_start', 'enable_cost_centres',
              'enable_budgets', 'enable_billwise_details', 'invoice_prefix',
              'stock_valuation_method', 'enable_audit_trail']
    template_name = 'finance/system_config.html'
    success_url = reverse_lazy('dashboard:index')

    def get_object(self, queryset=None):
        # Resolve the company — fall back to the first one if the user has no company FK
        company = getattr(self.request.user, 'company', None)
        if not company:
            from company.models import CompanyProfile
            company = CompanyProfile.objects.first()
        if not company:
            from django.http import Http404
            raise Http404("No company profile found. Please complete setup first.")
        obj, _ = SystemConfig.objects.get_or_create(company=company)
        return obj

    def form_valid(self, form):
        messages.success(self.request, 'System configuration updated successfully.')
        return super().form_valid(form)
