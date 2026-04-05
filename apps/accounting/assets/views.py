from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from company.models import CompanyProfile
from .models import FixedAsset

def get_user_company(request):
    if hasattr(request.user, "company") and request.user.company:
        return request.user.company
    return CompanyProfile.objects.first()

class FixedAssetListView(LoginRequiredMixin, ListView):
    model = FixedAsset
    template_name = 'accounting/assets/asset_list.html'
    context_object_name = 'assets'

    def get_queryset(self):
        company = get_user_company(self.request)
        if company:
            return FixedAsset.objects.filter(company=company)
        return FixedAsset.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assets = context['assets']
        context['total_cost'] = sum(a.purchase_value for a in assets)
        context['total_accum_depr'] = sum(a.accumulated_depreciation for a in assets)
        context['total_nbv'] = sum(a.net_book_value for a in assets)
        return context
