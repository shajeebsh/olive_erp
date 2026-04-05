from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from company.models import CompanyProfile
from tax_engine.models import TaxFiling

class CalendarEventsView(LoginRequiredMixin, View):
    def get(self, request):
        company = CompanyProfile.objects.get_current()
        filings = TaxFiling.objects.filter(company=company)
        events = []
        for f in filings:
            color = "#dc3545" if f.is_overdue else "#ffc107" if f.due_soon else "#198754"
            events.append({
                "title": f.get_filing_type_display(),
                "start": f.due_date.isoformat(),
                "url": f"/compliance/filings/{f.pk}/",
                "color": color,
            })
        return JsonResponse(events, safe=False)
