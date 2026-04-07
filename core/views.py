from django.shortcuts import render
from django.views.generic import View, ListView, View as DjangoView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from finance.models import Invoice, Account
from inventory.models import Product
from crm.models import Customer
from django.db.models import Q
from .models import ApprovalWorkflow, DocumentAttachment
from .utils import get_user_company

class GoToSearchView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        results = []
        if len(query) >= 2:
            # Search Invoices
            invoices = Invoice.objects.filter(
                Q(invoice_number__icontains=query) | Q(customer__company_name__icontains=query)
            )[:5]
            for inv in invoices:
                results.append({
                    'category': 'Invoices',
                    'title': f"Invoice {inv.invoice_number} - {inv.customer.company_name}",
                    'url': f"/finance/invoices/", # Simple link for now
                    'icon': 'fas fa-file-invoice-dollar'
                })

            # Search Products
            products = Product.objects.filter(name__icontains=query)[:5]
            for prod in products:
                results.append({
                    'category': 'Products',
                    'title': prod.name,
                    'url': f"/inventory/",
                    'icon': 'fas fa-box'
                })

            # Search Customers
            customers = Customer.objects.filter(company_name__icontains=query)[:5]
            for cust in customers:
                results.append({
                    'category': 'Customers',
                    'title': cust.company_name,
                    'url': f"/crm/",
                    'icon': 'fas fa-user-friends'
                })

        if request.headers.get('HX-Request'):
            return render(request, 'includes/search_results.html', {'results': results})

        return JsonResponse({'results': results})

def system_config(request):
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group
    User = get_user_model()
    context = {
        'config': {
            'f11_accounting': {'maintain_bill_wise': True, 'interest_calculation': False, 'maintain_cost_centre': True, 'maintain_budget': True},
            'f11_inventory': {'integrate_accounts': True, 'maintain_batch': True, 'multiple_uom': True, 'allow_negative_stock': False},
            'f11_statutory': {'country': 'AE', 'tax_system': 'vat', 'financial_year_start': '01-01'},
            'f12_general': {'date_format': 'dd-mm-yyyy', 'number_format': '1,234.00', 'currency_symbol': 'AED'},
            'f12_voucher': {'skip_date_field': False, 'single_entry_mode': False, 'warn_negative_cash': True}
        },
        'users': User.objects.all(),
        'roles': Group.objects.all()
    }
    return render(request, 'core/system_config.html', context)

def audit_log(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    context = {
        'users': User.objects.all(),
        'audit_logs': [
            {
                'id': 1, 'timestamp': '2025-01-20 10:00:00', 'user': request.user,
                'action': 'UPDATE', 'content_type': 'Invoice', 'object_repr': 'INV-2025-001',
                'ip_address': '192.168.1.5'
            },
            {
                'id': 2, 'timestamp': '2025-01-20 09:30:00', 'user': request.user,
                'action': 'CREATE', 'content_type': 'Customer', 'object_repr': 'Acme Corp',
                'ip_address': '192.168.1.5'
            }
        ]
    }
    return render(request, 'core/audit_log.html', context)


class ApprovalWorkflowListView(LoginRequiredMixin, ListView):
    """List all pending approvals for the user's company"""
    model = ApprovalWorkflow
    template_name = 'core/approval_list.html'
    context_object_name = 'approvals'
    
    def get_queryset(self):
        company = get_user_company(self.request)
        status_filter = self.request.GET.get('status', '')
        type_filter = self.request.GET.get('type', '')
        
        qs = ApprovalWorkflow.objects.filter(company=company)
        
        if status_filter:
            qs = qs.filter(status=status_filter)
        else:
            qs = qs.exclude(status='AP')  # Default: show pending and rejected
        
        if type_filter:
            qs = qs.filter(workflow_type=type_filter)
        
        return qs.select_related('requested_by', 'approved_by')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['type_filter'] = self.request.GET.get('type', '')
        context['workflow_types'] = ApprovalWorkflow.WORKFLOW_TYPES
        context['status_choices'] = ApprovalWorkflow.STATUS_CHOICES
        context['pending_count'] = self.get_queryset().filter(status='PE').count()
        return context


class ApprovalWorkflowDetailView(LoginRequiredMixin, DjangoView):
    """View approval details and take action"""
    
    def get(self, request, pk):
        approval = get_object_or_404(ApprovalWorkflow, pk=pk, company=get_user_company(request))
        return render(request, 'core/approval_detail.html', {'approval': approval})
    
    def post(self, request, pk):
        approval = get_object_or_404(ApprovalWorkflow, pk=pk, company=get_user_company(request))
        action = request.POST.get('action', '')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            approval.approve(request.user, notes)
            messages.success(request, f'Approved {approval.get_workflow_type_display()}')
        elif action == 'reject':
            approval.reject(request.user, notes)
            messages.warning(request, f'Rejected {approval.get_workflow_type_display()}')
        
        return redirect('core:approval_list')


def create_approval_request(request, workflow_type, model_name, object_id):
    """Create an approval workflow for a document requiring approval"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    company = get_user_company(request)
    
    # Check if approval already exists
    existing = ApprovalWorkflow.objects.filter(
        company=company,
        workflow_type=workflow_type,
        reference_model=model_name,
        object_id=object_id,
        status='PE'
    ).exists()
    
    if existing:
        return JsonResponse({'error': 'Approval already pending'}, status=400)
    
    # Create approval request
    approval = ApprovalWorkflow.objects.create(
        company=company,
        workflow_type=workflow_type,
        reference_id=str(object_id),
        reference_model=model_name,
        status='PE',
        requested_by=request.user,
        request_notes=request.POST.get('notes', '')
    )
    
    return JsonResponse({'success': True, 'approval_id': approval.id})


def upload_attachment(request):
    """Upload a document attachment to any model"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    from django.contrib.contenttypes.models import ContentType
    from .models import DocumentAttachment
    
    company = get_user_company(request)
    
    content_type_str = request.POST.get('content_type', '')
    try:
        app_label, model_name = content_type_str.split('.')
        content_type = ContentType.objects.get(app_label=app_label, model=model_name.lower())
    except (ValueError, ContentType.DoesNotExist):
        return JsonResponse({'error': 'Invalid content type'}, status=400)
    
    object_id = request.POST.get('object_id')
    file = request.FILES.get('file')
    description = request.POST.get('description', '')
    
    if not file or not object_id:
        return JsonResponse({'error': 'File and object_id required'}, status=400)
    
    attachment = DocumentAttachment.objects.create(
        company=company,
        content_type=content_type,
        object_id=object_id,
        file=file,
        filename=file.name,
        description=description,
        uploaded_by=request.user
    )
    
    messages.success(request, 'File uploaded successfully')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:index'))
