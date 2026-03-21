from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from compliance.mixins import CountryFilterMixin

class VAT3ReturnView(LoginRequiredMixin, CountryFilterMixin, TemplateView):
    template_name = "compliance/ie/vat3.html"
    required_country = "IE"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Pull T1-T9 box values from JournalEntry aggregates
        from finance.models import JournalEntry
        from django.db.models import Sum
        period = self.request.GET.get("period")  # e.g. "2024-Q1"
        ctx["boxes"] = {
            "T1": 0,   # VAT on sales (output tax)
            "T2": 0,   # VAT on purchases (input tax)
            "T3": 0,   # VAT payable (T1-T2 if positive)
            "T4": 0,   # VAT repayable (T2-T1 if positive)
            "T5": 0,   # Total goods/services supplied
            "T6": 0,   # Total goods/services received
            "T7": 0,   # Goods from EU (zero rated)
            "T8": 0,   # Goods to EU
            "T9": 0,   # Total transactions
        }
        ctx["period"] = period
        ctx["periods"] = ["2024-Q1","2024-Q2","2024-Q3","2024-Q4","2025-Q1","2025-Q2"]
        return ctx
