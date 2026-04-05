from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from tax_engine.mixins import CountryFilterMixin
from tax_engine.models import TaxFiling, TaxPeriod
from company.models import CompanyProfile
from django.utils import timezone

class ComplianceDashboardView(LoginRequiredMixin, CountryFilterMixin, TemplateView):
    template_name = "tax_engine/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        company = CompanyProfile.objects.get_current()
        country = company.country_code
        now = timezone.now()

        ctx["company"] = company
        ctx["country_code"] = country
        ctx["pending_filings"] = TaxFiling.objects.filter(
            company=company, status__in=["draft", "pending"]
        ).order_by("due_date")[:10]
        ctx["overdue_filings"] = TaxFiling.objects.filter(
            company=company, status__in=["draft", "pending"], due_date__lt=now
        ).count()
        ctx["filed_this_year"] = TaxFiling.objects.filter(
            company=company, status="filed", due_date__year=now.year
        ).count()
        ctx["upcoming_deadlines"] = TaxFiling.objects.filter(
            company=company,
            status__in=["draft", "pending"],
            due_date__gte=now,
            due_date__lte=now + timezone.timedelta(days=30),
        ).order_by("due_date")[:5]
        return ctx
