from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, TemplateView

from .forms import CompanyProfileForm, FeatureSelectionForm
from .models import CompanyProfile, Currency


class CompanySetupView(LoginRequiredMixin, FormView):
    template_name = "company/setup/step1_company.html"
    form_class = CompanyProfileForm
    success_url = reverse_lazy("company:setup_features")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        instance = CompanyProfile.objects.first()
        if instance:
            kwargs.update({"instance": instance})
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        self.request.session["company_id"] = self.object.id
        return super().form_valid(form)


class SetupStep2View(LoginRequiredMixin, FormView):
    """Step 2: Select country and configure features"""

    template_name = "company/setup/step2.html"
    form_class = FeatureSelectionForm
    success_url = reverse_lazy("company:setup_step3")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from compliance.registry import registry

        # Get all available countries
        context["countries"] = registry.get_all_countries()

        # Get selected country from session
        context["selected_country"] = self.request.session.get("setup_country", "IE")

        return context

    def form_valid(self, form):
        # Store country selection in session
        self.request.session["setup_country"] = form.cleaned_data["country"]
        self.request.session["setup_features"] = form.cleaned_data["features"]

        # Ensure country_code is stored in CompanyProfile
        if hasattr(self.request.user, "company") and self.request.user.company:
            company = self.request.user.company
            company.country_code = form.cleaned_data["country"]
            company.save()
        elif CompanyProfile.objects.exists():
            # Fallback for systems with singleton-like CompanyProfile
            company = CompanyProfile.objects.first()
            company.country_code = form.cleaned_data["country"]
            company.save()

        return super().form_valid(form)


class SetupStep3View(LoginRequiredMixin, TemplateView):
    """Step 3: Country-specific configuration"""

    template_name = "company/setup/step3.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        country_code = self.request.session.get("setup_country", "IE")

        from compliance.registry import registry

        engine = registry.get_tax_engine(country_code)

        if engine:
            context["country"] = {
                "code": country_code,
                "name": engine.country_name,
                "tax_name": engine.tax_name,
                "currency": engine.currency_code,
                "tax_rates": engine.get_tax_rates(),
            }

        return context

    def post(self, request, *args, **kwargs):
        country_code = request.session.get("setup_country", "IE")
        tax_number = request.POST.get("tax_number")

        from compliance.registry import registry

        is_valid, message = registry.validate_tax_number(country_code, tax_number)

        if not is_valid:
            messages.error(request, message)
            return self.get(request, *args, **kwargs)

        # Store in company profile (will be saved in final step)
        request.session["setup_tax_number"] = tax_number
        request.session["setup_tax_rates"] = request.POST.get("selected_rates")

        return redirect("company:setup_complete")


class SetupCompleteView(LoginRequiredMixin, TemplateView):
    template_name = "company/setup/complete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = CompanyProfile.objects.first()
        return context


def profile(request):
    company = CompanyProfile.objects.first()
    return render(request, "company/profile.html", {"company": company})
