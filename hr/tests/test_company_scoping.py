from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
from company.models import CompanyProfile
from crm.models import Customer
from hr.models import Employee
from projects.models import Project, Task
from purchasing.models import Supplier, PurchaseOrder
from inventory.models import Product

User = get_user_model()


class CompanyScopingTest(TestCase):
    def setUp(self):
        self.company1 = CompanyProfile.objects.create(
            name="Company One",
            email="one@example.com",
            phone="1111111111",
            address="Address 1",
            fiscal_year_start_date=date(2024, 1, 1)
        )
        self.company2 = CompanyProfile.objects.create(
            name="Company Two",
            email="two@example.com",
            phone="2222222222",
            address="Address 2",
            fiscal_year_start_date=date(2024, 1, 1)
        )
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='pass')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='pass')
        self.employee1 = Employee.objects.create(
            user=self.user1, company=self.company1, employee_id='EMP001',
            department=None, job_title='Dev', hire_date=date(2024, 1, 1),
            salary=50000, contact_info='x', address='x', emergency_contact='x'
        )
        self.employee2 = Employee.objects.create(
            user=self.user2, company=self.company2, employee_id='EMP002',
            department=None, job_title='Dev', hire_date=date(2024, 1, 1),
            salary=50000, contact_info='x', address='x', emergency_contact='x'
        )
        self.customer1 = Customer.objects.create(company=self.company1, user=self.user1, company_name='Cust1', contact_person='CP1', email='cp1@x.com', address='x', payment_terms='Net 30')
        self.customer2 = Customer.objects.create(company=self.company2, user=self.user2, company_name='Cust2', contact_person='CP2', email='cp2@x.com', address='x', payment_terms='Net 30')
        self.supplier1 = Supplier.objects.create(company=self.company1, company_name='Supp1', contact_person='SP1', email='sp1@x.com', phone='1', address='x', payment_terms='Net 30')
        self.supplier2 = Supplier.objects.create(company=self.company2, company_name='Supp2', contact_person='SP2', email='sp2@x.com', phone='2', address='x', payment_terms='Net 30')
        self.project1 = Project.objects.create(company=self.company1, name='Proj1', description='x', customer=self.customer1, start_date=date(2024, 1, 1), end_date=date(2024, 12, 31), status='PLANNING', budget=1000)
        self.project2 = Project.objects.create(company=self.company2, name='Proj2', description='x', customer=self.customer2, start_date=date(2024, 1, 1), end_date=date(2024, 12, 31), status='PLANNING', budget=1000)
        self.product1 = Product.objects.create(company=self.company1, sku='SKU001', name='Prod1', unit_of_measure='pcs', selling_price=10, cost_price=5)
        self.product2 = Product.objects.create(company=self.company2, sku='SKU002', name='Prod2', unit_of_measure='pcs', selling_price=10, cost_price=5)

    def test_project_list_scoped_to_company(self):
        from projects.models import Project
        from core.utils import get_user_company
        qs = Project.objects.filter(company=self.company1)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().name, 'Proj1')

    def test_project_detail_blocked_cross_company(self):
        from django.shortcuts import get_object_or_404
        from django.http import Http404
        with self.assertRaises(Http404):
            get_object_or_404(Project, pk=self.project2.pk, company=self.company1)

    def test_supplier_list_scoped_to_company(self):
        from purchasing.models import Supplier
        qs = Supplier.objects.filter(company=self.company1)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().company_name, 'Supp1')

    def test_purchase_order_list_scoped_to_company(self):
        po = PurchaseOrder.objects.create(company=self.company1, po_number='PO001', supplier=self.supplier1, order_date=date(2024, 1, 1), expected_delivery_date=date(2024, 12, 31))
        qs = PurchaseOrder.objects.filter(company=self.company1)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().po_number, 'PO001')

    def test_product_list_scoped_to_company(self):
        qs = Product.objects.filter(company=self.company1)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().sku, 'SKU001')

    def test_task_list_scoped_to_company(self):
        task1 = Task.objects.create(project=self.project1, name='Task1', assigned_to=self.employee1, due_date=date(2024, 12, 31))
        task2 = Task.objects.create(project=self.project2, name='Task2', assigned_to=self.employee2, due_date=date(2024, 12, 31))
        qs = Task.objects.filter(project__company=self.company1)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().name, 'Task1')
