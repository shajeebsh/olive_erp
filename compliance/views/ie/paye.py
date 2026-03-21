from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from compliance.mixins import CountryFilterMixin

class PAYEView(LoginRequiredMixin, CountryFilterMixin, TemplateView):
    template_name = "compliance/ie/paye.html"
    required_country = "IE"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Mock payroll data
        ctx["period"] = "July 2024"
        ctx["gross_pay"] = "45000.00"
        ctx["paye_deducted"] = "8500.00"
        ctx["prsi_employee"] = "1800.00"
        ctx["prsi_employer"] = "4950.00"
        ctx["usc_deducted"] = "2100.00"
        
        ctx["total_due"] = float(ctx["paye_deducted"]) + float(ctx["prsi_employee"]) + float(ctx["prsi_employer"]) + float(ctx["usc_deducted"])
        return ctx
