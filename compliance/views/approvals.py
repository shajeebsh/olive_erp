from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from compliance.mixins import CountryFilterMixin
from compliance.models import FilingApproval, TaxFiling
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone

class ApprovalsView(LoginRequiredMixin, CountryFilterMixin, ListView):
    model = FilingApproval
    template_name = "compliance/approvals.html"
    context_object_name = "approvals"

    def get_queryset(self):
        # Create missing approvals for any draft/pending TaxFilings
        filings = TaxFiling.objects.filter(company=self.company).exclude(status='filed')
        for filing in filings:
            FilingApproval.objects.get_or_create(filing=filing)
            
        return FilingApproval.objects.filter(
            filing__company=self.company
        ).exclude(stage='filed').select_related('filing')

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        approval_id = request.POST.get('approval_id')
        comment = request.POST.get('comment', '')
        
        approval = get_object_or_404(FilingApproval, pk=approval_id, filing__company=self.company)
        filing = approval.filing
        
        if action == 'submit_review' and approval.stage == 'prepare':
            approval.stage = 'cfo'
            filing.status = 'pending'
            messages.success(request, f"Submitted {filing} for CFO Review.")
            
        elif action == 'cfo_approve' and approval.stage == 'cfo':
            approval.stage = 'board'
            approval.cfo_approved_by = request.user
            messages.success(request, f"CFO approved {filing}. Sent to Board.")
            
        elif action == 'cfo_reject' and approval.stage == 'cfo':
            approval.stage = 'prepare'
            filing.status = 'draft'
            approval.notes = f"{approval.notes}\nRejected by CFO: {comment}"
            messages.warning(request, f"CFO rejected {filing}.")
            
        elif action == 'board_approve' and approval.stage == 'board':
            approval.stage = 'filed'
            approval.board_approved_by = request.user
            filing.status = 'approved'
            messages.success(request, f"Board approved {filing}. Ready to file.")
            
        elif action == 'board_reject' and approval.stage == 'board':
            approval.stage = 'prepare'
            filing.status = 'draft'
            approval.notes = f"{approval.notes}\nRejected by Board: {comment}"
            messages.warning(request, f"Board rejected {filing}.")
            
        elif action == 'mark_filed' and approval.stage == 'filed':
            ref = request.POST.get('reference', '')
            filing.status = 'filed'
            filing.reference = ref
            filing.filed_date = timezone.now().date()
            approval.filed_reference = ref
            messages.success(request, f"Marked {filing} as filed!")
            
        approval.save()
        filing.save()
        return redirect('compliance:approvals')
