from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class CountryFilterMixin:
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'company') or not request.user.company:
            return redirect('company:setup')
        kwargs['country_code'] = request.user.company.country_code
        return super().dispatch(request, *args, **kwargs)

def cro_b1(request):
    return render(request, 'compliance/cro_b1.html')

def ct1(request):
    return render(request, 'compliance/ct1.html')

def vat(request):
    return render(request, 'compliance/vat.html')

def rbo(request):
    return render(request, 'compliance/rbo.html')

def paye(request):
    return render(request, 'compliance/paye.html')

def calendar(request):
    return render(request, 'compliance/calendar.html')

def history(request):
    return render(request, 'compliance/history.html')

def dashboard(request):
    if not hasattr(request.user, 'company') or not request.user.company:
        return redirect('company:setup')
    return render(request, 'compliance/dashboard.html', {'company': request.user.company})

def return_preview(request, return_id=None):
    if not hasattr(request.user, 'company') or not request.user.company:
        return redirect('company:setup')
        
    company = request.user.company
    # Mock data for template filtered by company country
    context = {
        'company': company,
        'country_code': company.country_code,
        'form_name': 'Return',
        'period': {'start': '2025-01-01', 'end': '2025-03-31'},
        'form_template': 'compliance/mock_form.html',
        'boxes': {}
    }
    return render(request, 'compliance/return_preview.html', context)

def approval_workflow(request):
    if not hasattr(request.user, 'company') or not request.user.company:
        return redirect('company:setup')
        
    company = request.user.company
    from django.contrib.auth import get_user_model
    User = get_user_model()
    first_user = User.objects.first() or request.user
    
    context = {
        'company': company,
        'pending_returns': [
            {
                'id': 1, 'country_code': company.country_code, 'form_name': 'Tax Return',
                'period_start': '2025-01-01', 'period_end': '2025-03-31',
                'preparer': first_user, 'currency': 'Local',
                'net_payable': '0.00', 'current_stage': 'Review'
            }
        ],
        'approval_history': []
    }
    return render(request, 'compliance/approval_workflow.html', context)
