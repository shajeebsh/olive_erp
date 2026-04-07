from django.test import TestCase
from django.urls import reverse
from company.models import CompanyProfile
from tax_engine.models import TaxFiling, FilingApproval
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime

class ComplianceAppTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test_user', password='password123')
        # Setup company - the CompanyProfile uses get_current which expects 1 active profile initially
        # Let's clean up existing if any just in case, though in tests it should be empty
        CompanyProfile.objects.all().delete()
        self.company = CompanyProfile.objects.create(
            name='Test IE Corp',
            country_code='IE',
            fiscal_year_start_date=datetime.date(2024, 1, 1)
        )
        
    def test_dashboard_kpis(self):
        """Test the dashboard KPIs accurately count TaxFilings based on status/due_dates."""
        now = timezone.now()
        TaxFiling.objects.create(
            company=self.company,
            filing_type='vat_return',
            period='2024-Q1',
            due_date=now.date() + datetime.timedelta(days=10),
            status='pending'
        )
        TaxFiling.objects.create(
            company=self.company,
            filing_type='corp_tax',
            period='2023',
            due_date=now.date() - datetime.timedelta(days=5),
            status='draft'
        )

        self.client.login(username='test_user', password='password123')
        url = reverse('tax_engine:dashboard')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pending_filings'].count(), 2)
        self.assertEqual(response.context['overdue_filings'], 1)
        self.assertEqual(response.context['upcoming_deadlines'].count(), 1)
        
    def test_approvals_workflow(self):
        """Test the approvals advancing logic."""
        self.client.login(username='test_user', password='password123')
        
        filing = TaxFiling.objects.create(
            company=self.company, filing_type='vat_return',
            period='2024-Q2', due_date=timezone.now().date(), status='draft'
        )
        approval = FilingApproval.objects.create(filing=filing, stage='prepare')
        
        url = reverse('tax_engine:approvals')
        
        # 1. Prepare to CFO Review
        response = self.client.post(url, {
            'action': 'submit_review',
            'approval_id': approval.id
        })
        self.assertEqual(response.status_code, 302)
        
        approval.refresh_from_db()
        filing.refresh_from_db()
        self.assertEqual(approval.stage, 'cfo')
        self.assertEqual(filing.status, 'pending')

        # 2. CFO Approve to Board Approval
        response = self.client.post(url, {
            'action': 'cfo_approve',
            'approval_id': approval.id
        })
        approval.refresh_from_db()
        self.assertEqual(approval.stage, 'board')
        
        # 3. Board Reject to Prepare
        response = self.client.post(url, {
            'action': 'board_reject',
            'approval_id': approval.id,
            'comment': 'Needs revision'
        })
        approval.refresh_from_db()
        filing.refresh_from_db()
        self.assertEqual(approval.stage, 'prepare')
        self.assertEqual(filing.status, 'draft')
        self.assertIn('Rejected by Board', approval.notes)

    def test_country_filter_mixin(self):
        """Test CountryFilterMixin restricts access if company.country_code doesn't match."""
        # Change company to UK
        self.company.country_code = 'UK'
        self.company.save()
        
        self.client.login(username='test_user', password='password123')
        url = reverse('tax_engine:ie_vat3')
        
        # VAT3 demands 'IE', user has 'UK'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403) # PermissionDenied
