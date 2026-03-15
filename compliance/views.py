from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View


class CountryFilterMixin:
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, "company") or not request.user.company:
            # Try to get first company if user doesn't have one directly linked
            from company.models import CompanyProfile

            company = CompanyProfile.objects.first()
            if not company:
                return redirect("company:setup")
            request.user.company = company

        kwargs["country_code"] = request.user.company.country_code
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = (
            super().get_context_data(**kwargs)
            if hasattr(super(), "get_context_data")
            else {}
        )
        context["company"] = self.request.user.company
        return context


class ComplianceDashboardView(LoginRequiredMixin, CountryFilterMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        # Add mock data for dashboard counts
        context.update(
            {
                "pending_count": 3,
                "filed_count": 12,
                "due_soon_count": 2,
                "overdue_count": 1,
                "pending_filings": [
                    {
                        "form_name": "VAT Return",
                        "period": "2025-Q1",
                        "due_date": "2025-04-20",
                        "status": "Due Soon",
                        "status_color": "warning",
                        "prepare_url": "#",
                    }
                ],
            }
        )
        return render(request, "compliance/dashboard.html", context)


def cro_b1(request):
    return render(
        request,
        "compliance/cro_b1.html",
        {"company": request.user.company if hasattr(request.user, "company") else None},
    )


def ct1(request):
    return render(
        request,
        "compliance/ct1.html",
        {"company": request.user.company if hasattr(request.user, "company") else None},
    )


def vat(request):
    return render(
        request,
        "compliance/vat.html",
        {"company": request.user.company if hasattr(request.user, "company") else None},
    )


def rbo(request):
    return render(
        request,
        "compliance/rbo.html",
        {"company": request.user.company if hasattr(request.user, "company") else None},
    )


def paye(request):
    return render(
        request,
        "compliance/paye.html",
        {"company": request.user.company if hasattr(request.user, "company") else None},
    )


def calendar(request):
    return render(
        request,
        "compliance/calendar.html",
        {"company": request.user.company if hasattr(request.user, "company") else None},
    )


def history(request):
    return render(
        request,
        "compliance/history.html",
        {"company": request.user.company if hasattr(request.user, "company") else None},
    )


def return_preview(request, return_id=None):
    # Mock data for template
    context = {
        "country_flag": "🇦🇪",
        "country_name": "UAE",
        "form_name": "VAT201",
        "period": {"start": "2025-01-01", "end": "2025-03-31"},
        "form_template": "compliance/mock_form.html",
        "boxes": {},
    }
    return render(request, "compliance/return_preview.html", context)


def approval_workflow(request):
    # Mock data for template
    from django.contrib.auth import get_user_model

    User = get_user_model()
    first_user = User.objects.first() or request.user

    context = {
        "pending_returns": [
            {
                "id": 1,
                "country_flag": "🇦🇪",
                "form_name": "VAT201",
                "period_start": "2025-01-01",
                "period_end": "2025-03-31",
                "preparer": first_user,
                "currency": "AED",
                "net_payable": "5000.00",
                "current_stage": "CFO Review",
            }
        ],
        "approval_history": [
            {
                "form_name": "IE VAT3",
                "period": "2024-Q4",
                "approver": first_user,
                "date": "2025-01-15",
            }
        ],
    }
    return render(request, "compliance/approval_workflow.html", context)
