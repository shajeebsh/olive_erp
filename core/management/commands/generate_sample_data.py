import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker

from company.models import CompanyProfile, Currency
from finance.models import Account, Invoice, JournalEntry, JournalEntryLine
from inventory.models import Category, Product, Warehouse, StockLevel, StockMovement
from crm.models import Customer, SalesOrder, SalesOrderLine
from hr.models import Department, Employee, LeaveRequest, Attendance
from projects.models import Project, Task
from purchasing.models import Supplier, PurchaseOrder, PurchaseOrderLine, GoodsReceivedNote
from compliance.models import TaxPeriod, Filing, FinancialStatement, BeneficialOwner

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates realistic sample data for Olive ERP modules'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Wipe existing sample data before generating new data',
        )
        parser.add_argument(
            '--num-months',
            type=int,
            default=12,
            help='Number of months of historical data to generate (default: 12)',
        )

    def handle(self, *args, **options):
        self.fake = Faker(['en_IE'])
        self.clear_existing = options['clear_existing']
        self.num_months = options['num_months']
        
        self.stdout.write("Starting sample data generation...")

        if self.clear_existing:
            self.stdout.write("Warning: --clear-existing is set. Wiping database...")
            self.clear_database()

        # Generate data step by step
        self.admin_user = self.get_or_create_admin()
        self.company, self.currency = self.generate_company()
        self.accounts = self.generate_accounts()
        self.warehouses = self.generate_warehouses()
        self.categories, self.products = self.generate_inventory()
        self.customers = self.generate_crm()
        self.departments, self.employees = self.generate_hr()
        self.projects = self.generate_projects()
        self.suppliers = self.generate_purchasing()
        
        # Generate transactional data over time
        self.generate_transactions()
        self.generate_compliance()

        self.stdout.write(self.style.SUCCESS("Successfully generated sample data!"))

    def clear_database(self):
        # Ordered by foreign key dependencies
        BeneficialOwner.objects.all().delete()
        FinancialStatement.objects.all().delete()
        Filing.objects.all().delete()
        TaxPeriod.objects.all().delete()
        
        GoodsReceivedNote.objects.all().delete()
        PurchaseOrderLine.objects.all().delete()
        PurchaseOrder.objects.all().delete()
        Supplier.objects.all().delete()

        Task.objects.all().delete()
        Project.objects.all().delete()

        Attendance.objects.all().delete()
        LeaveRequest.objects.all().delete()
        Employee.objects.all().delete()
        Department.objects.all().delete()

        SalesOrderLine.objects.all().delete()
        SalesOrder.objects.all().delete()
        Invoice.objects.all().delete()
        Customer.objects.all().delete()

        StockMovement.objects.all().delete()
        StockLevel.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Warehouse.objects.all().delete()

        JournalEntryLine.objects.all().delete()
        JournalEntry.objects.all().delete()
        Account.objects.all().delete()

        CompanyProfile.objects.all().delete()
        Currency.objects.all().delete()
        self.stdout.write("Database cleared.")

    def get_or_create_admin(self):
        user, created = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@olivetech.ie',
            'is_staff': True,
            'is_superuser': True
        })
        if created:
            user.set_password('admin')
            user.save()
        return user

    def generate_company(self):
        self.stdout.write("Generating Company...")
        currency, _ = Currency.objects.get_or_create(
            code="EUR", defaults={'name': 'Euro', 'symbol': '€', 'exchange_rate_to_base': 1.0}
        )
        company, _ = CompanyProfile.objects.get_or_create(
            name="Olive Tech Solutions Ltd",
            defaults={
                'address': "123 Main Street, Dublin, Ireland",
                'phone': "+353 1 234 5678",
                'email': "info@olivetech.ie",
                'website': "www.olivetech.ie",
                'tax_id': "IE1234567A",
                'fiscal_year_start_date': "2026-01-01",
                'default_currency': currency
            }
        )
        return company, currency

    def generate_accounts(self):
        self.stdout.write("Generating Chart of Accounts...")
        accounts = {}
        top_level = [
            ('1000', 'Assets', 'ASSET'),
            ('2000', 'Liabilities', 'LIABILITY'),
            ('3000', 'Equity', 'EQUITY'),
            ('4000', 'Income', 'INCOME'),
            ('5000', 'Expenses', 'EXPENSE')
        ]
        
        for code, name, acc_type in top_level:
            acc, _ = Account.objects.get_or_create(code=code, defaults={'name': name, 'type': acc_type, 'company': self.company})
            accounts[code] = acc
            
        # Assets
        accounts['1100'], _ = Account.objects.get_or_create(code='1100', defaults={'name': 'Current Assets', 'type': 'ASSET', 'parent': accounts['1000'], 'company': self.company})
        accounts['1110'], _ = Account.objects.get_or_create(code='1110', defaults={'name': 'Bank Accounts', 'type': 'ASSET', 'parent': accounts['1100'], 'company': self.company})
        accounts['1120'], _ = Account.objects.get_or_create(code='1120', defaults={'name': 'Accounts Receivable', 'type': 'ASSET', 'parent': accounts['1100'], 'company': self.company})
        accounts['1130'], _ = Account.objects.get_or_create(code='1130', defaults={'name': 'Inventory', 'type': 'ASSET', 'parent': accounts['1100'], 'company': self.company})
        accounts['1200'], _ = Account.objects.get_or_create(code='1200', defaults={'name': 'Fixed Assets', 'type': 'ASSET', 'parent': accounts['1000'], 'company': self.company})
        
        # Liabilities
        accounts['2100'], _ = Account.objects.get_or_create(code='2100', defaults={'name': 'Current Liabilities', 'type': 'LIABILITY', 'parent': accounts['2000'], 'company': self.company})
        accounts['2110'], _ = Account.objects.get_or_create(code='2110', defaults={'name': 'Accounts Payable', 'type': 'LIABILITY', 'parent': accounts['2100'], 'company': self.company})
        accounts['2120'], _ = Account.objects.get_or_create(code='2120', defaults={'name': 'Taxes Payable', 'type': 'LIABILITY', 'parent': accounts['2100'], 'company': self.company})
        
        # Equity
        accounts['3100'], _ = Account.objects.get_or_create(code='3100', defaults={'name': 'Capital', 'type': 'EQUITY', 'parent': accounts['3000'], 'company': self.company})
        accounts['3200'], _ = Account.objects.get_or_create(code='3200', defaults={'name': 'Retained Earnings', 'type': 'EQUITY', 'parent': accounts['3000'], 'company': self.company})
        
        # Income
        accounts['4100'], _ = Account.objects.get_or_create(code='4100', defaults={'name': 'Sales Revenue', 'type': 'INCOME', 'parent': accounts['4000'], 'company': self.company})
        accounts['4200'], _ = Account.objects.get_or_create(code='4200', defaults={'name': 'Other Income', 'type': 'INCOME', 'parent': accounts['4000'], 'company': self.company})
        
        # Expenses
        accounts['5100'], _ = Account.objects.get_or_create(code='5100', defaults={'name': 'Cost of Goods Sold', 'type': 'EXPENSE', 'parent': accounts['5000'], 'company': self.company})
        accounts['5200'], _ = Account.objects.get_or_create(code='5200', defaults={'name': 'Operating Expenses', 'type': 'EXPENSE', 'parent': accounts['5000'], 'company': self.company})
        accounts['5210'], _ = Account.objects.get_or_create(code='5210', defaults={'name': 'Payroll Expenses', 'type': 'EXPENSE', 'parent': accounts['5200'], 'company': self.company})
        accounts['5220'], _ = Account.objects.get_or_create(code='5220', defaults={'name': 'Rent', 'type': 'EXPENSE', 'parent': accounts['5200'], 'company': self.company})

        return accounts

    def generate_warehouses(self):
        self.stdout.write("Generating Warehouses...")
        warehouses = []
        for loc in ['Dublin', 'Cork', 'Galway']:
            w, _ = Warehouse.objects.get_or_create(name=f"{loc} Warehouse", defaults={'location': f"{loc}, Ireland"})
            warehouses.append(w)
        return warehouses

    def generate_inventory(self):
        self.stdout.write("Generating Inventory (100+ products)...")
        cat_names = ['Electronics', 'Furniture', 'Office Supplies', 'Software', 'Hardware', 'Networking', 'Peripherals', 'Services', 'Accessories', 'Components']
        categories = []
        for name in cat_names:
            c, _ = Category.objects.get_or_create(name=name, defaults={'description': f"{name} items"})
            categories.append(c)

        products = []
        for i in range(100):
            cat = random.choice(categories)
            price = Decimal(random.uniform(10.0, 2000.0)).quantize(Decimal('0.01'))
            cost = (price * Decimal(random.uniform(0.4, 0.8))).quantize(Decimal('0.01'))
            
            p, _ = Product.objects.get_or_create(
                sku=f"SKU-{cat.name[:3].upper()}-{1000+i}",
                defaults={
                    'name': f"{self.fake.word().title()} {cat.name[:-1]}",
                    'description': self.fake.text(max_nb_chars=100),
                    'category': cat,
                    'unit_of_measure': random.choice(['pcs', 'boxes', 'kg']),
                    'selling_price': price,
                    'cost_price': cost,
                    'tax_rate': Decimal('23.00')
                }
            )
            products.append(p)
            
            # Stock levels
            for w in self.warehouses:
                qty = Decimal(random.randint(0, 500))
                StockLevel.objects.get_or_create(product=p, warehouse=w, defaults={'quantity_on_hand': qty, 'reorder_level': Decimal(random.randint(10, 50))})

        return categories, products

    def generate_crm(self):
        self.stdout.write("Generating CRM Customers...")
        customers = []
        for i in range(50):
            is_company = random.choice([True, False])
            user, _ = User.objects.get_or_create(username=f"customer_{i}", defaults={'email': self.fake.email()})
            c, _ = Customer.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': self.fake.company() if is_company else "",
                    'contact_person': self.fake.name(),
                    'email': user.email,
                    'phone': self.fake.phone_number()[:20],
                    'address': self.fake.address(),
                    'tax_number': f"IE{random.randint(1000000, 9999999)}A" if is_company else "",
                    'payment_terms': random.choice(['Net 15', 'Net 30', 'CIA'])
                }
            )
            customers.append(c)
        return customers

    def generate_hr(self):
        self.stdout.write("Generating HR Departments and Employees...")
        dept_names = ['Executive', 'Sales', 'Engineering', 'Marketing', 'HR', 'Finance', 'Operations', 'IT']
        departments = []
        for name in dept_names:
            d, _ = Department.objects.get_or_create(name=name, defaults={'description': f"{name} Department"})
            departments.append(d)

        employees = []
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=3*365) # 3 years ago

        for i in range(42):
            user, _ = User.objects.get_or_create(username=f"emp_{i}", defaults={'email': f"emp{i}@olivetech.ie", 'first_name': self.fake.first_name(), 'last_name': self.fake.last_name()})
            hire_date = self.fake.date_between(start_date=start_date, end_date=end_date)
            
            emp, _ = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': f"EMP-{1000+i}",
                    'department': random.choice(departments),
                    'job_title': self.fake.job(),
                    'hire_date': hire_date,
                    'salary': Decimal(random.randint(35000, 120000)),
                    'contact_info': self.fake.phone_number(),
                    'address': self.fake.address(),
                    'emergency_contact': f"{self.fake.name()} - {self.fake.phone_number()}"
                }
            )
            employees.append(emp)
        return departments, employees

    def generate_projects(self):
        self.stdout.write("Generating Projects...")
        projects = []
        end_date = timezone.now().date()
        for i in range(15):
            p_start = self.fake.date_between(start_date=end_date - timedelta(days=300), end_date=end_date)
            p_end = p_start + timedelta(days=random.randint(30, 180))
            status = random.choice(['PLANNING', 'IN_PROGRESS', 'ON_HOLD', 'COMPLETED'])
            
            p, _ = Project.objects.get_or_create(
                name=f"Project {self.fake.bs().title()}",
                defaults={
                    'description': self.fake.text(),
                    'customer': random.choice(self.customers),
                    'start_date': p_start,
                    'end_date': p_end,
                    'status': status,
                    'budget': Decimal(random.randint(10000, 250000))
                }
            )
            projects.append(p)
            
            # Create tasks for this project
            for t in range(random.randint(5, 20)):
                Task.objects.get_or_create(
                    project=p,
                    name=self.fake.catch_phrase(),
                    defaults={
                        'assigned_to': random.choice(self.employees),
                        'due_date': p_start + timedelta(days=random.randint(1, 40)),
                        'status': random.choice(['TODO', 'IN_PROGRESS', 'DONE']),
                        'hours_logged': Decimal(random.uniform(0, 40)).quantize(Decimal('0.01'))
                    }
                )
        return projects

    def generate_purchasing(self):
        self.stdout.write("Generating Suppliers...")
        suppliers = []
        for i in range(25):
            s, _ = Supplier.objects.get_or_create(
                company_name=self.fake.company(),
                defaults={
                    'contact_person': self.fake.name(),
                    'email': self.fake.company_email(),
                    'phone': self.fake.phone_number()[:20],
                    'address': self.fake.address(),
                    'tax_number': f"IE{random.randint(1000000, 9999999)}B",
                    'payment_terms': 'Net 30'
                }
            )
            suppliers.append(s)
        return suppliers

    def generate_transactions(self):
        self.stdout.write("Generating Transactions (Invoices, Sales Orders, Purchase Orders, Journals, HR Records)...")
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30 * self.num_months)

        # HR Attendance & Leave
        for emp in self.employees:
            # Leave
            for _ in range(random.randint(0, 3)):
                l_start = self.fake.date_between(start_date=start_date, end_date=end_date)
                LeaveRequest.objects.get_or_create(
                    employee=emp,
                    leave_type=random.choice(['SICK', 'VACATION', 'OTHER']),
                    start_date=l_start,
                    end_date=l_start + timedelta(days=random.randint(1, 5)),
                    defaults={
                        'status': random.choice(['PENDING', 'APPROVED', 'REJECTED']),
                        'reason': self.fake.sentence()
                    }
                )

        # Sales Orders & Invoices (100+)
        for i in range(100):
            order_date = self.fake.date_between(start_date=start_date, end_date=end_date)
            cust = random.choice(self.customers)
            status = random.choice(['QUOTE', 'DRAFT', 'CONFIRMED', 'SHIPPED', 'INVOICED'])
            
            so, _ = SalesOrder.objects.get_or_create(
                order_number=f"SO-{order_date.year}-{1000+i}",
                defaults={
                    'customer': cust,
                    'order_date': order_date,
                    'expected_delivery_date': order_date + timedelta(days=random.randint(5, 15)),
                    'status': status,
                    'notes': self.fake.sentence()
                }
            )
            
            total_amount = Decimal('0.00')
            for _ in range(random.randint(1, 5)):
                prod = random.choice(self.products)
                qty = Decimal(random.randint(1, 10))
                price = prod.selling_price * qty
                total_amount += price
                SalesOrderLine.objects.get_or_create(
                    sales_order=so,
                    product=prod,
                    defaults={
                        'quantity': qty,
                        'unit_price': prod.selling_price,
                        'total_price': price
                    }
                )
            
            so.total_amount = total_amount
            so.save()

            # If invoiced, create invoice and journal
            if status in ['SHIPPED', 'INVOICED'] or random.random() > 0.5:
                # 50+ invoices
                inv_status = random.choice(['DRAFT', 'SENT', 'PAID', 'OVERDUE'])
                inv_date = order_date + timedelta(days=2)
                inv, created = Invoice.objects.get_or_create(
                    invoice_number=f"INV-{inv_date.year}-{1000+i}",
                    defaults={
                        'customer': cust,
                        'issue_date': inv_date,
                        'due_date': inv_date + timedelta(days=30),
                        'total_amount': total_amount,
                        'tax_amount': (total_amount * Decimal('0.23')).quantize(Decimal('0.01')),
                        'status': inv_status
                    }
                )

                if created and inv_status in ['SENT', 'PAID']:
                    # Create Journal Entry
                    je = JournalEntry.objects.create(
                        entry_number=f"JE-INV-{inv.invoice_number}",
                        date=inv_date,
                        description=f"Invoice {inv.invoice_number} to {cust.company_name or cust.contact_person}",
                        created_by=self.admin_user,
                        is_posted=True
                    )
                    # Debit AR
                    JournalEntryLine.objects.create(journal_entry=je, account=self.accounts['1120'], debit=total_amount + inv.tax_amount)
                    # Credit Sales Rev
                    JournalEntryLine.objects.create(journal_entry=je, account=self.accounts['4100'], credit=total_amount)
                    # Credit Taxes Payable
                    JournalEntryLine.objects.create(journal_entry=je, account=self.accounts['2120'], credit=inv.tax_amount)
                    
            # Stock Movements for Sales
            if status in ['SHIPPED', 'INVOICED']:
                for line in so.lines.all():
                    StockMovement.objects.create(
                        product=line.product,
                        warehouse=random.choice(self.warehouses),
                        quantity=-line.quantity,
                        movement_type='SALE',
                        reference=f"SO#{so.order_number}",
                        created_by=self.admin_user
                    )

        # Purchase Orders (75)
        for i in range(75):
            order_date = self.fake.date_between(start_date=start_date, end_date=end_date)
            sup = random.choice(self.suppliers)
            po, created = PurchaseOrder.objects.get_or_create(
                po_number=f"PO-{order_date.year}-{1000+i}",
                defaults={
                    'supplier': sup,
                    'order_date': order_date,
                    'expected_delivery_date': order_date + timedelta(days=random.randint(7, 21)),
                    'status': random.choice(['SENT', 'PARTIALLY_RECEIVED', 'RECEIVED']),
                    'total_amount': Decimal('0.00')
                }
            )
            
            if created:
                total_amount = Decimal('0.00')
                for _ in range(random.randint(1, 5)):
                    prod = random.choice(self.products)
                    qty = Decimal(random.randint(10, 100))
                    price = prod.cost_price * qty
                    total_amount += price
                    qty_received = qty if po.status == 'RECEIVED' else Decimal('0.00')
                    PurchaseOrderLine.objects.create(
                        purchase_order=po, product=prod, quantity=qty, unit_price=prod.cost_price, 
                        total_price=price, quantity_received=qty_received
                    )
                
                po.total_amount = total_amount
                po.save()

                if po.status == 'RECEIVED':
                    grn = GoodsReceivedNote.objects.create(
                        grn_number=f"GRN-{po.po_number}",
                        purchase_order=po,
                        received_by=self.admin_user
                    )
                    for line in po.lines.all():
                        StockMovement.objects.create(
                            product=line.product,
                            warehouse=random.choice(self.warehouses),
                            quantity=line.quantity,
                            movement_type='PURCHASE',
                            reference=f"GRN#{grn.grn_number}",
                            created_by=self.admin_user
                        )

    def generate_compliance(self):
        self.stdout.write("Generating Compliance Data...")
        end_date = timezone.now().date()
        
        # Create a tax period
        tp, _ = TaxPeriod.objects.get_or_create(
            company=self.company,
            start_date=end_date.replace(month=1, day=1) - timedelta(days=365),
            end_date=end_date.replace(month=12, day=31) - timedelta(days=365),
            defaults={'period_type': 'ANNUAL', 'is_closed': True}
        )
        
        # Draft CT1
        Filing.objects.get_or_create(
            company=self.company,
            tax_period=tp,
            filing_type='CT',
            defaults={
                'status': 'DRAFT',
                'due_date': end_date + timedelta(days=90),
                'amount_due': Decimal('15000.00')
            }
        )

        # RBO Beneficial Owners
        BeneficialOwner.objects.get_or_create(
            company=self.company,
            owner_type='INDIVIDUAL',
            name=self.fake.name(),
            defaults={'address': self.fake.address(), 'nationality': 'Irish'}
        )
