from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from company.models import CompanyProfile
from finance.models import Account, JournalEntry, JournalEntryLine
from apps.accounting.compliance.models import RelatedPartyTransaction as ComplianceRPT
from apps.accounting.related_party.models import RelatedPartyTransaction as JournalRPT
from datetime import date
from decimal import Decimal

User = get_user_model()

class RelatedPartyReportingTest(TestCase):
    def setUp(self):
        self.company = CompanyProfile.objects.create(
            name="Test Company",
            country_code="IE",
            fiscal_year_start_date=date(2026, 1, 1)
        )
        self.other_company = CompanyProfile.objects.create(
            name="Other Company",
            country_code="IE",
            fiscal_year_start_date=date(2026, 1, 1)
        )
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )
        self.client = Client()
        self.client.login(username='admin', password='password')

        # 1. Create a compliance-based RPT
        self.compliance_rpt = ComplianceRPT.objects.create(
            company=self.company,
            party_name="Director A",
            relationship="Director",
            transaction_date=date(2026, 3, 1),
            transaction_nature="Loan",
            amount=Decimal('5000.00'),
            is_arm_length=True
        )

        # 2. Create a journal-linked RPT
        self.account = Account.objects.create(
            code="4000",
            name="Director Loan Account",
            account_type="Liability",
            company=self.company
        )
        self.journal = JournalEntry.objects.create(
            entry_number="JE-001",
            date=date(2026, 3, 15),
            description="Loan from Director",
            is_posted=True,
            created_by=self.user
        )
        self.line = JournalEntryLine.objects.create(
            journal_entry=self.journal,
            account=self.account,
            description="Loan amount",
            debit=0,
            credit=Decimal('10000.00')
        )
        self.journal_rpt = JournalRPT.objects.create(
            journal_entry_line=self.line,
            relationship_type="director_related",
            notes="Formalized loan agreement"
        )

        # 3. Create a record for another company to test scoping
        ComplianceRPT.objects.create(
            company=self.other_company,
            party_name="Other Party",
            relationship="Associate",
            transaction_date=date(2026, 3, 1),
            amount=Decimal('100.00')
        )

    def test_related_party_list_view(self):
        """Verify the report correctly aggregates data from both models and respects company scoping."""
        url = reverse('accounting:related_party_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        transactions = response.context['transactions']
        
        # Should have exactly 2 transactions for this company
        self.assertEqual(len(transactions), 2)
        
        # Verify compliance RPT data
        comp_data = next(t for t in transactions if t['party_name'] == "Director A")
        self.assertEqual(comp_data['amount'], Decimal('5000.00'))
        self.assertEqual(comp_data['relationship'], "Director")
        
        # Verify journal-linked RPT data
        # Note: In the view, the amount is taken from credit/debit
        journ_data = next(t for t in transactions if t['amount'] == Decimal('10000.00'))
        self.assertEqual(journ_data['party_name'], "Director Loan Account") # Uses account name
        self.assertEqual(journ_data['relationship'], "director_related")
        
        # Verify no data from other company
        self.assertFalse(any(t['party_name'] == "Other Party" for t in transactions))

    def test_view_no_crashing(self):
        """Ensure the view renders correctly even with missing optional data."""
        url = reverse('accounting:related_party_list')
        response = self.client.get(url)
        self.assertContains(response, "Director A")
        self.assertContains(response, "Director Loan Account")
