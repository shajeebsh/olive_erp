from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CompanyProfile, Currency
from .forms import CompanyProfileForm


class CompanySetupView(LoginRequiredMixin, CreateView):
    model = CompanyProfile
    form_class = CompanyProfileForm
    template_name = 'company/setup/step1_company.html'
    success_url = reverse_lazy('company:setup_features')

    def dispatch(self, request, *args, **kwargs):
        if CompanyProfile.objects.exists():
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session['company_id'] = self.object.id
        return response


class FeatureSetupView(LoginRequiredMixin, TemplateView):
    template_name = 'company/setup/step2_features.html'

    def dispatch(self, request, *args, **kwargs):
        if not CompanyProfile.objects.exists():
            return redirect('company:setup')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        load_sample = request.POST.get('load_sample_data') == 'on'
        if load_sample:
            # We will handle calling the command in a clean way or advise manual run
            # For this MVP, we capture the preference or just redirect
            pass
            
        return redirect('dashboard:index')


def profile(request):
    company = CompanyProfile.objects.first()
    return render(request, 'company/profile.html', {'company': company})
