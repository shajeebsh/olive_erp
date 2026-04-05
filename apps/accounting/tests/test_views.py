from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from company.models import CompanyProfile
from finance.models import Account
from apps.accounting.reconciliation.models import BankReconciliation
from datetime import date

User = get_user_model()

class AccountingViewTest(TestCase):
    def setUp(self):
        self.company = CompanyProfile.objects.create(
            name="Test Company",
            country_code="IE",
            email="test@example.com",
            address="123 Test St",
            phone="1234567890",
            fiscal_year_start_date=date(2026, 1, 1)
        )
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )
        self.client = Client()
        self.account = Account.objects.create(
            code="1020",
            name="Bank",
            account_type="Asset",
            company=self.company
        )

    def test_profit_loss_view_status(self):
        self.client.login(username='admin', password='password')
        url = reverse('accounting:profit_loss')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_balance_sheet_view_status(self):
        self.client.login(username='admin', password='password')
        url = reverse('accounting:balance_sheet')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reconciliation_view_status(self):
        self.client.login(username='admin', password='password')
        url = reverse('accounting:bank_reconciliation')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_access(self):
        url = reverse('accounting:profit_loss')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302) # Redirect to login
