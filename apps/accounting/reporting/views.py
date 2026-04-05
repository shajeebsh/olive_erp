from django.views.generic import TemplateView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.utils import timezone
from django.http import HttpResponse
from django.urls import reverse_lazy
from datetime import date
from company.models import CompanyProfile
from finance.models import Account, JournalEntryLine
from reporting.engines import ReportEngine
from apps.accounting.reconciliation.models import BankReconciliation
from apps.accounting.compliance.models import CT1Computation

def get_user_company(request):
    if hasattr(request.user, "company") and request.user.company:
        return request.user.company
    return CompanyProfile.objects.first()

from decimal import Decimal

class ProfitAndLossView(LoginRequiredMixin, TemplateView):
    template_name = 'accounting/reporting/profit_loss.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        company = get_user_company(self.request)
        start = self.request.GET.get('start_date')
        end   = self.request.GET.get('end_date')
        
        qs = JournalEntryLine.objects.filter(journal_entry__is_posted=True, account__company=company)
        if start: qs = qs.filter(journal_entry__date__gte=start)
        if end:   qs = qs.filter(journal_entry__date__lte=end)

        def cat_total(acc_type, cat_name):
            # Aggregating Credit - Debit for Income, Debit - Credit for Expense
            agg = qs.filter(account__account_type=acc_type, account__name__icontains=cat_name).aggregate(
                d=Sum('debit'), c=Sum('credit')
            )
            debit = agg['d'] or Decimal('0')
            credit = agg['c'] or Decimal('0')
            if acc_type == 'Income':
                return credit - debit
            return debit - credit

        INCOME_CATS  = ['Sales Revenue', 'Other Income']
        COGS_CATS    = ['Cost of Goods Sold']
        EXPENSE_CATS = ['Payroll','Rent','Utilities','IT & Software',
                        'Office Expenses','Travel & Subsistence',
                        'Marketing','Professional Fees','Bank Charges',
                        'Insurance','Telephone & Internet',
                        'Depreciation','Miscellaneous']

        income_rows  = [(c, cat_total('Income',  c)) for c in INCOME_CATS]
        cogs_rows    = [(c, cat_total('Expense', c)) for c in COGS_CATS]
        expense_rows = [(c, cat_total('Expense', c)) for c in EXPENSE_CATS]

        total_income   = sum(v for _,v in income_rows)
        total_cogs     = sum(v for _,v in cogs_rows)
        gross_profit   = total_income - total_cogs
        total_expenses = sum(v for _,v in expense_rows)
        net_profit     = gross_profit - total_expenses

        ctx.update({
            'income_rows': income_rows, 'cogs_rows': cogs_rows,
            'expense_rows': expense_rows, 'total_income': total_income,
            'total_cogs': total_cogs, 'gross_profit': gross_profit,
            'total_expenses': total_expenses, 'net_profit': net_profit,
            'start_date': start, 'end_date': end
        })
        return ctx

class BalanceSheetView(LoginRequiredMixin, TemplateView):
    template_name = 'accounting/reporting/balance_sheet.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        company = get_user_company(self.request)
        as_of = self.request.GET.get('as_of_date')
        
        qs = JournalEntryLine.objects.filter(journal_entry__is_posted=True, account__company=company)
        if as_of: qs = qs.filter(journal_entry__date__lte=as_of)

        def sumifs(acc_type, cat_name=None):
            q = qs.filter(account__account_type=acc_type)
            if cat_name: q = q.filter(account__name__icontains=cat_name)
            agg = q.aggregate(d=Sum('debit'), c=Sum('credit'))
            debit = agg['d'] or Decimal('0')
            credit = agg['c'] or Decimal('0')
            if acc_type in ['Asset', 'Expense']:
                return debit - credit
            return credit - debit

        # Assets
        # Cash & Bank: Asset accounts with 'Bank' or 'Cash' in name
        cash_bank = sumifs('Asset', 'Bank') + sumifs('Asset', 'Cash')
        accounts_receivable = sumifs('Asset', 'Accounts Receivable')
        
        # Fixed Assets NBV
        try:
            from apps.accounting.assets.models import FixedAsset
            fixed_assets_nbv = sum(a.book_value for a in FixedAsset.objects.filter(company=company))
        except:
            fixed_assets_nbv = sumifs('Asset', 'Fixed Assets')

        total_assets = cash_bank + accounts_receivable + fixed_assets_nbv

        # Liabilities
        accounts_payable = sumifs('Liability', 'Accounts Payable')
        total_liabilities = accounts_payable

        # Equity
        capital = sumifs('Equity', 'Capital')
        drawings = sumifs('Equity', 'Drawings')
        # Retained Earnings = Total Income - Total Expense up to date (excluding capital/drawings)
        retained = sumifs('Income') - sumifs('Expense')
        
        total_equity = capital - drawings + retained

        # Balance check
        balance_check = abs(total_assets - total_liabilities - total_equity) < Decimal('0.01')

        ctx.update({
            'cash_bank': cash_bank, 'accounts_receivable': accounts_receivable,
            'fixed_assets_nbv': fixed_assets_nbv, 'total_assets': total_assets,
            'accounts_payable': accounts_payable, 'total_liabilities': total_liabilities,
            'capital': capital, 'drawings': drawings, 'retained': retained,
            'total_equity': total_equity, 'balance_check': balance_check,
            'as_of_date': as_of
        })
        return ctx

class VATSummaryView(LoginRequiredMixin, TemplateView):
    template_name = 'accounting/reporting/vat_summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = get_user_company(self.request)
        
        # Aggregate VAT components from JournalEntryLine
        vat_lines = JournalEntryLine.objects.filter(
            account__company=company,
            account__name__icontains='VAT'
        )
        
        context['vat_summary'] = vat_lines.values('account__name').annotate(
            total_debit=Sum('debit'),
            total_credit=Sum('credit'),
            net_vat=Sum('credit') - Sum('debit')
        )
        context['company_profile'] = company
        
        # Calculate VAT threshold status
        from datetime import date, timedelta
        from dateutil.relativedelta import relativedelta
        
        # Get sales in last 12 months
        twelve_months_ago = date.today() - relativedelta(months=12)
        sales_total = JournalEntryLine.objects.filter(
            account__company=company,
            account__account_type='Income',
            journal_entry__date__gte=twelve_months_ago,
            journal_entry__is_posted=True
        ).aggregate(total=Sum('credit'))['total'] or Decimal('0')
        
        threshold = company.vat_services_threshold if company.vat_registered else Decimal('42500')
        percentage = (float(sales_total) / float(threshold) * 100) if threshold > 0 else 0
        
        context['vat_threshold_current'] = sales_total
        context['vat_threshold_limit'] = threshold
        context['vat_threshold_percentage'] = min(round(percentage, 1), 100)
        context['vat_threshold_status'] = 'danger' if percentage >= 100 else ('warning' if percentage >= 80 else 'success')
        
        return context

class BankReconciliationView(LoginRequiredMixin, ListView):
    model = BankReconciliation
    template_name = 'accounting/reporting/bank_reconciliation.html'
    context_object_name = 'reconciliations'

    def get_queryset(self):
        return BankReconciliation.objects.filter(company=get_user_company(self.request))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        reconciliations = self.get_queryset()
        ctx['year_total_income']   = sum(r.period_income   for r in reconciliations)
        ctx['year_total_expenses'] = sum(r.period_expenses for r in reconciliations)
        return ctx

class CT1ComputationView(LoginRequiredMixin, ListView):
    model = CT1Computation
    template_name = 'accounting/reporting/ct1_list.html'
    context_object_name = 'computations'

    def get_queryset(self):
        return CT1Computation.objects.filter(company=get_user_company(self.request))


class CT1CreateView(LoginRequiredMixin, TemplateView):
    template_name = 'accounting/reporting/ct1_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        company = get_user_company(self.request)
        
        # Calculate accounting profit from P&L
        lines = JournalEntryLine.objects.filter(
            journal_entry__is_posted=True,
            account__company=company
        )
        
        total_income = lines.filter(account__account_type='Income').aggregate(
            total=Sum('credit') - Sum('debit'))['total'] or Decimal('0')
        
        total_expenses = lines.filter(account__account_type='Expense').aggregate(
            total=Sum('debit') - Sum('credit'))['total'] or Decimal('0')
        
        net_profit = total_income - total_expenses
        
        ctx['accounting_profit'] = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_profit': net_profit
        }
        
        return ctx

class StatutoryRegisterView(LoginRequiredMixin, TemplateView):
    template_name = 'accounting/reporting/statutory_registers.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        company = get_user_company(self.request)
        from tax_engine.countries.ie.models import Director, Secretary, Shareholder
        from tax_engine.countries.ie.rbo import BeneficialOwner
        
        ctx['directors'] = Director.objects.filter(company=company)
        ctx['secretaries'] = Secretary.objects.filter(company=company)
        ctx['shareholders'] = Shareholder.objects.filter(company=company)
        ctx['beneficial_owners'] = BeneficialOwner.objects.filter(company=company)
        return ctx

class DividendListView(LoginRequiredMixin, ListView):
    template_name = 'accounting/reporting/dividend_list.html'
    context_object_name = 'dividends'

    def get_queryset(self):
        return []  # Dividend model not yet implemented

class RelatedPartyTransactionView(LoginRequiredMixin, ListView):
    template_name = 'accounting/reporting/related_party_list.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        from apps.accounting.related_party.models import RelatedPartyTransaction
        return RelatedPartyTransaction.objects.filter(journal_entry_line__account__company=get_user_company(self.request))


class BankReconciliationUpdateView(LoginRequiredMixin, TemplateView):
    """HTMX endpoint for inline updating bank reconciliation entries"""
    template_name = 'accounting/reporting/includes/recon_row.html'

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            recon = BankReconciliation.objects.get(pk=pk, company=get_user_company(request))
        except BankReconciliation.DoesNotExist:
            return HttpResponse('Not found', status=404)

        opening_balance = request.POST.get('opening_balance')
        actual_closing_balance = request.POST.get('actual_closing_balance')
        notes = request.POST.get('notes')

        if opening_balance:
            recon.opening_balance = opening_balance
        if actual_closing_balance:
            recon.actual_closing_balance = actual_closing_balance
        if notes is not None:
            recon.notes = notes

        # Auto-update status based on difference
        if recon.difference == 0:
            recon.status = 'RC'
        elif recon.actual_closing_balance is not None:
            recon.status = 'DC'

        recon.save()

        context = self.get_context_data()
        context['recon'] = recon
        return self.render_to_response(context)
