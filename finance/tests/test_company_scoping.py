from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from finance.views import InvoiceListView, JournalEntryListView, ExpenseListView, InvoiceCreateView, InvoiceUpdateView
from company.models import CompanyProfile
from finance.models import Account, Invoice, InvoiceTemplate
from crm.models import Customer
from datetime import date

User = get_user_model()


class TestCompanyScoping(TestCase):
    """Test that finance views properly scope data by company."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.company1 = CompanyProfile.objects.create(
            name='Company One',
            address='Address 1',
            phone='123',
            email='company1@test.com',
            fiscal_year_start_date=date(2024, 1, 1)
        )
        
        self.company2 = CompanyProfile.objects.create(
            name='Company Two',
            address='Address 2',
            phone='456',
            email='company2@test.com',
            fiscal_year_start_date=date(2024, 1, 1)
        )
        
        self.user.company = self.company1
        self.user.save()
        
        self.expense_account1 = Account.objects.create(
            code='600',
            name='Test Expense',
            account_type='Expense',
            company=self.company1
        )
        
        self.expense_account2 = Account.objects.create(
            code='601',
            name='Other Expense',
            account_type='Expense',
            company=self.company2
        )
    
    def test_expense_list_scoped_to_company(self):
        """ExpenseListView should only return expense accounts for user's company."""
        request = self.factory.get('/finance/expenses/')
        request.user = self.user
        
        view = ExpenseListView()
        view.request = request
        
        qs = view.get_queryset()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), self.expense_account1)
        self.assertNotIn(self.expense_account2, qs)
    
    def test_expense_list_excludes_other_company_accounts(self):
        """Expense accounts from other companies should not appear in results."""
        Account.objects.create(
            code='602',
            name='Company 2 Expense',
            account_type='Expense',
            company=self.company2
        )

        request = self.factory.get('/finance/expenses/')
        request.user = self.user

        view = ExpenseListView()
        view.request = request

        qs = view.get_queryset()
        self.assertEqual(qs.count(), 1)
        self.assertTrue(all(acc.company == self.company1 for acc in qs))


class TestInvoiceCompanyScoping(TestCase):
    """Test that invoice views and forms properly scope data by company."""

    def setUp(self):
        from django.contrib.auth import get_user_model

        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='invoicetest',
            email='invoice@test.com',
            password='testpass123'
        )

        self.company1 = CompanyProfile.objects.create(
            name='Invoice Company One',
            address='Address 1',
            phone='123',
            email='inv1@test.com',
            fiscal_year_start_date=date(2024, 1, 1)
        )

        self.company2 = CompanyProfile.objects.create(
            name='Invoice Company Two',
            address='Address 2',
            phone='456',
            email='inv2@test.com',
            fiscal_year_start_date=date(2024, 1, 1)
        )

        self.user.company = self.company1
        self.user.save()

        self.customer_user = get_user_model().objects.create_user(
            username='customeruser',
            email='customer@test.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.customer_user,
            contact_person='John Doe',
            email='john@test.com',
            phone='1234567890',
            address='123 Test St'
        )

        self.template1 = InvoiceTemplate.objects.create(
            name='Standard',
            company=self.company1,
            template_html='<html>Invoice</html>'
        )

        self.template2 = InvoiceTemplate.objects.create(
            name='Other Company Template',
            company=self.company2,
            template_html='<html>Other Invoice</html>'
        )

        self.invoice1 = Invoice.objects.create(
            invoice_number='INV-2024-001',
            customer=self.customer,
            invoice_template=self.template1,
            company=self.company1,
            issue_date=date(2024, 1, 1),
            due_date=date(2024, 1, 31),
            total_amount=1000.00,
            tax_amount=100.00,
            status='DRAFT'
        )

    def test_invoice_create_assigns_company(self):
        """InvoiceCreateView should assign the active company to new invoices."""
        request = self.factory.get('/finance/invoice/add/')
        request.user = self.user
        request.session = {'company_id': self.company1.id}

        view = InvoiceCreateView()
        view.request = request

        kwargs = view.get_form_kwargs()
        self.assertEqual(kwargs['company'], self.company1)

    def test_invoice_update_scoped_to_company(self):
        """InvoiceUpdateView should only allow editing invoices for user's company."""
        request = self.factory.get(f'/finance/invoice/{self.invoice1.pk}/change/')
        request.user = self.user
        request.session = {'company_id': self.company1.id}

        view = InvoiceUpdateView()
        view.request = request

        qs = view.get_queryset()
        self.assertIn(self.invoice1, qs)

        other_company_invoice = Invoice.objects.create(
            invoice_number='INV-2024-002',
            customer=self.customer,
            invoice_template=self.template2,
            company=self.company2,
            issue_date=date(2024, 1, 1),
            due_date=date(2024, 1, 31),
            total_amount=2000.00,
            tax_amount=200.00,
            status='DRAFT'
        )

        self.assertNotIn(other_company_invoice, qs)

    def test_invoice_form_filters_invoice_template(self):
        """InvoiceForm should only show invoice templates for the active company."""
        from finance.forms import InvoiceForm

        form = InvoiceForm(company=self.company1)
        template_ids = list(form.fields['invoice_template'].queryset.values_list('id', flat=True))

        self.assertIn(self.template1.id, template_ids)
        self.assertNotIn(self.template2.id, template_ids)

    def test_invoice_list_scoped_to_company(self):
        """InvoiceListView should only return invoices for user's company."""
        request = self.factory.get('/finance/invoices/')
        request.user = self.user
        request.session = {'company_id': self.company1.id}

        view = InvoiceListView()
        view.request = request

        qs = view.get_queryset()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), self.invoice1)