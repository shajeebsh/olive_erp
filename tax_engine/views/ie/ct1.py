from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from tax_engine.mixins import CountryFilterMixin

class CT1ReturnView(LoginRequiredMixin, CountryFilterMixin, TemplateView):
    template_name = "tax_engine/ie/ct1.html"
    required_country = "IE"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        period = self.request.GET.get("period", "2023")
        ctx["period"] = period
        ctx["periods"] = ["2022", "2023", "2024"]
        ctx["trading_income"] = 0
        ctx["capital_allowances"] = 0
        ctx["taxable_income"] = 0
        ctx["corp_tax_payable"] = 0
        return ctx
