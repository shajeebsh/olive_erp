from django.core.exceptions import PermissionDenied
from company.models import CompanyProfile

class CountryFilterMixin:
    required_country = None  # Set on views that are country-specific

    def dispatch(self, request, *args, **kwargs):
        company = CompanyProfile.objects.get_current()
        if self.required_country and company.country_code != self.required_country:
            raise PermissionDenied(
                f"This page is only available for {self.required_country} companies."
            )
        self.company = company
        return super().dispatch(request, *args, **kwargs)
