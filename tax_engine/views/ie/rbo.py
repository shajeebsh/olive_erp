from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from tax_engine.mixins import CountryFilterMixin

class RBOView(LoginRequiredMixin, CountryFilterMixin, TemplateView):
    template_name = "tax_engine/ie/rbo.html"
    required_country = "IE"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["bo_list"] = [
            {"name": "John Doe", "pps": "1234567A", "dob": "1980-05-15", "pct": "60%"},
            {"name": "Jane Smith", "pps": "7654321B", "dob": "1985-08-22", "pct": "40%"},
        ]
        return ctx
