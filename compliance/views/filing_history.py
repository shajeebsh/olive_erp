from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from compliance.mixins import CountryFilterMixin
from compliance.models import TaxFiling

class FilingHistoryView(LoginRequiredMixin, CountryFilterMixin, ListView):
    model = TaxFiling
    template_name = "compliance/filings.html"
    context_object_name = "filings"
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().filter(company=self.company).order_by("-due_date")
        
        # Apply filters if present in request.GET
        filing_type = self.request.GET.get('type')
        if filing_type:
            qs = qs.filter(filing_type=filing_type)
            
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
            
        year = self.request.GET.get('year')
        if year:
            qs = qs.filter(due_date__year=year)
            
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filing_types'] = TaxFiling.FILING_TYPES
        ctx['statuses'] = TaxFiling.STATUS
        ctx['current_type'] = self.request.GET.get('type', '')
        ctx['current_status'] = self.request.GET.get('status', '')
        ctx['current_year'] = self.request.GET.get('year', '')
        return ctx

class FilingDetailView(LoginRequiredMixin, CountryFilterMixin, DetailView):
    model = TaxFiling
    template_name = "compliance/filing_detail.html"
    context_object_name = "filing"

    def get_queryset(self):
        return super().get_queryset().filter(company=self.company)
