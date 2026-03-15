from django.shortcuts import render


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

from datetime import date
def dashboard(request):
    return render(request, 'compliance/dashboard.html')

def return_preview(request, return_id=None):
    # Mock data for template
    context = {
        'country_flag': '🇦🇪',
        'country_name': 'UAE',
        'form_name': 'VAT201',
        'period': {'start': '2025-01-01', 'end': '2025-03-31'},
        'form_template': 'compliance/mock_form.html',
        'boxes': {}
    }
    return render(request, 'compliance/return_preview.html', context)

def approval_workflow(request):
    # Mock data for template
    from django.contrib.auth import get_user_model
    User = get_user_model()
    first_user = User.objects.first() or request.user
    
    context = {
        'pending_returns': [
            {
                'id': 1, 'country_flag': '🇦🇪', 'form_name': 'VAT201',
                'period_start': '2025-01-01', 'period_end': '2025-03-31',
                'preparer': first_user, 'currency': 'AED',
                'net_payable': '5000.00', 'current_stage': 'CFO Review'
            }
        ],
        'approval_history': [
            {
                'form_name': 'IE VAT3', 'period': '2024-Q4',
                'approver': first_user, 'date': '2025-01-15'
            }
        ]
    }
    return render(request, 'compliance/approval_workflow.html', context)

def consolidated_reports(request):
    return render(request, 'compliance/consolidated_reports.html')
