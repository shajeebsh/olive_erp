from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from tax_engine.mixins import CountryFilterMixin

class CROB1View(LoginRequiredMixin, CountryFilterMixin, TemplateView):
    template_name = "tax_engine/ie/cro_b1.html"
    required_country = "IE"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        company = CompanyProfile.objects.get_current()
        ctx["company"] = company
        ctx["ard"] = "2024-09-30" # Mock ARD
        return ctx
