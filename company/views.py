from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CompanyProfile, Currency
from .forms import CompanyProfileForm


class CompanySetupView(LoginRequiredMixin, FormView):
    template_name = 'company/setup/step1_company.html'
    form_class = CompanyProfileForm
    success_url = reverse_lazy('company:setup_features')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        instance = CompanyProfile.objects.first()
        if instance:
            kwargs.update({'instance': instance})
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        self.request.session['company_id'] = self.object.id
        return super().form_valid(form)


class FeatureSetupView(LoginRequiredMixin, TemplateView):
    template_name = 'company/setup/step2_features.html'

    def dispatch(self, request, *args, **kwargs):
        if not CompanyProfile.objects.exists():
            return redirect('company:setup')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        load_sample = request.POST.get('load_sample_data') == 'on'
        if load_sample:
            # In a real scenario, we might trigger a background task
            # For this MVP, we redirect to a completion page that handles it or provides instructions
            pass
            
        return redirect('company:setup_complete')


class SetupCompleteView(LoginRequiredMixin, TemplateView):
    template_name = 'company/setup/complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = CompanyProfile.objects.first()
        return context


def profile(request):
    company = CompanyProfile.objects.first()
    return render(request, 'company/profile.html', {'company': company})
