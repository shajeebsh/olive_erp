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
from tax_engine.models import TaxPeriod, TaxFiling, BeneficialOwner
from apps.accounting.assets.models import FixedAsset
from apps.accounting.reconciliation.models import BankReconciliation
from apps.accounting.compliance.models import ComplianceDeadline, CT1Computation, Dividend

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
        TaxFiling.objects.all().delete()
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
        from datetime import date
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
                'fiscal_year_start_date': date(2026, 1, 1),
                'default_currency': currency
            }
        )
        return company, currency

    def generate_accounts(self):
        self.stdout.write("Generating Chart of Accounts...")
        accounts = {}
        top_level = [
            ('1000', 'Assets', 'Asset'),
            ('2000', 'Liabilities', 'Liability'),
            ('3000', 'Equity', 'Equity'),
            ('4000', 'Income', 'Income'),
            ('5000', 'Expenses', 'Expense')
        ]
        
        for code, name, acc_type in top_level:
            acc, _ = Account.objects.get_or_create(code=code, defaults={'name': name, 'account_type': acc_type, 'company': self.company})
            accounts[code] = acc
            
        # Assets
        accounts['1100'], _ = Account.objects.get_or_create(code='1100', defaults={'name': 'Current Assets', 'account_type': 'Asset', 'parent': accounts['1000'], 'company': self.company})
        accounts['1110'], _ = Account.objects.get_or_create(code='1110', defaults={'name': 'Bank Accounts', 'account_type': 'Asset', 'parent': accounts['1100'], 'company': self.company})
        accounts['1120'], _ = Account.objects.get_or_create(code='1120', defaults={'name': 'Accounts Receivable', 'account_type': 'Asset', 'parent': accounts['1100'], 'company': self.company})
        accounts['1130'], _ = Account.objects.get_or_create(code='1130', defaults={'name': 'Inventory', 'account_type': 'Asset', 'parent': accounts['1100'], 'company': self.company})
        accounts['1200'], _ = Account.objects.get_or_create(code='1200', defaults={'name': 'Fixed Assets', 'account_type': 'Asset', 'parent': accounts['1000'], 'company': self.company})
        
        # Liabilities
        accounts['2100'], _ = Account.objects.get_or_create(code='2100', defaults={'name': 'Current Liabilities', 'account_type': 'Liability', 'parent': accounts['2000'], 'company': self.company})
        accounts['2110'], _ = Account.objects.get_or_create(code='2110', defaults={'name': 'Accounts Payable', 'account_type': 'Liability', 'parent': accounts['2100'], 'company': self.company})
        accounts['2120'], _ = Account.objects.get_or_create(code='2120', defaults={'name': 'VAT Payable', 'account_type': 'Liability', 'parent': accounts['2100'], 'company': self.company})
        
        # Equity
        accounts['3100'], _ = Account.objects.get_or_create(code='3100', defaults={'name': 'Capital', 'account_type': 'Equity', 'parent': accounts['3000'], 'company': self.company})
        accounts['3200'], _ = Account.objects.get_or_create(code='3200', defaults={'name': 'Retained Earnings', 'account_type': 'Equity', 'parent': accounts['3000'], 'company': self.company})
        
        # Income
        accounts['4100'], _ = Account.objects.get_or_create(code='4100', defaults={'name': 'Sales Revenue', 'account_type': 'Income', 'parent': accounts['4000'], 'company': self.company})
        accounts['4110'], _ = Account.objects.get_or_create(code='4110', defaults={'name': 'Consulting Services', 'account_type': 'Income', 'parent': accounts['4100'], 'company': self.company})
        accounts['4200'], _ = Account.objects.get_or_create(code='4200', defaults={'name': 'Other Income', 'account_type': 'Income', 'parent': accounts['4000'], 'company': self.company})
        accounts['4210'], _ = Account.objects.get_or_create(code='4210', defaults={'name': 'Interest Income', 'account_type': 'Income', 'parent': accounts['4200'], 'company': self.company})
        
        # Expenses
        accounts['5100'], _ = Account.objects.get_or_create(code='5100', defaults={'name': 'Cost of Goods Sold', 'account_type': 'Expense', 'parent': accounts['5000'], 'company': self.company})
        accounts['5200'], _ = Account.objects.get_or_create(code='5200', defaults={'name': 'Operating Expenses', 'account_type': 'Expense', 'parent': accounts['5000'], 'company': self.company})
        accounts['5210'], _ = Account.objects.get_or_create(code='5210', defaults={'name': 'Payroll Expenses', 'account_type': 'Expense', 'parent': accounts['5200'], 'company': self.company})
        accounts['5220'], _ = Account.objects.get_or_create(code='5220', defaults={'name': 'Rent', 'account_type': 'Expense', 'parent': accounts['5200'], 'company': self.company})
        accounts['5230'], _ = Account.objects.get_or_create(code='5230', defaults={'name': 'Utilities', 'account_type': 'Expense', 'parent': accounts['5200'], 'company': self.company})
        accounts['5240'], _ = Account.objects.get_or_create(code='5240', defaults={'name': 'IT & Software', 'account_type': 'Expense', 'parent': accounts['5200'], 'company': self.company})
        accounts['5250'], _ = Account.objects.get_or_create(code='5250', defaults={'name': 'Professional Fees', 'account_type': 'Expense', 'parent': accounts['5200'], 'company': self.company})
        accounts['5260'], _ = Account.objects.get_or_create(code='5260', defaults={'name': 'Travel & Subsistence', 'account_type': 'Expense', 'parent': accounts['5200'], 'company': self.company})
        accounts['5270'], _ = Account.objects.get_or_create(code='5270', defaults={'name': 'Marketing', 'account_type': 'Expense', 'parent': accounts['5200'], 'company': self.company})
        accounts['5280'], _ = Account.objects.get_or_create(code='5280', defaults={'name': 'Insurance', 'account_type': 'Expense', 'parent': accounts['5200'], 'company': self.company})
        accounts['5290'], _ = Account.objects.get_or_create(code='5290', defaults={'name': 'Depreciation', 'account_type': 'Expense', 'parent': accounts['5200'], 'company': self.company})
        
        # VAT Accounts
        accounts['2130'], _ = Account.objects.get_or_create(code='2130', defaults={'name': 'VAT Receivable', 'account_type': 'Asset', 'parent': accounts['1100'], 'company': self.company})
        
        # Add more detailed Fixed Assets accounts
        accounts['1210'], _ = Account.objects.get_or_create(code='1210', defaults={'name': 'Computer Equipment', 'account_type': 'Asset', 'parent': accounts['1200'], 'company': self.company})
        accounts['1220'], _ = Account.objects.get_or_create(code='1220', defaults={'name': 'Office Furniture', 'account_type': 'Asset', 'parent': accounts['1200'], 'company': self.company})
        accounts['1230'], _ = Account.objects.get_or_create(code='1230', defaults={'name': 'Vehicles', 'account_type': 'Asset', 'parent': accounts['1200'], 'company': self.company})
        accounts['1290'], _ = Account.objects.get_or_create(code='1290', defaults={'name': 'Accumulated Depreciation', 'account_type': 'Asset', 'parent': accounts['1200'], 'company': self.company})

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
            country='IE',
            start_date=end_date.replace(month=1, day=1) - timedelta(days=365),
            end_date=end_date.replace(month=12, day=31) - timedelta(days=365),
            defaults={
                'period_type': 'annual',
                'status': 'filed'
            }
        )
        
        # Draft CT1 Tax Filing
        TaxFiling.objects.get_or_create(
            company=self.company,
            filing_type='CT1',
            period=f'{end_date.year - 1}',
            defaults={
                'status': 'draft',
                'due_date': end_date + timedelta(days=90),
            }
        )

        # RBO Beneficial Owners - just use first_name/last_name for lookup
        from datetime import date
        BeneficialOwner.objects.get_or_create(
            company=self.company,
            first_name=self.fake.first_name(),
            last_name=self.fake.last_name(),
            defaults={
                'date_of_birth': date(1980, 1, 1),
                'became_owner_date': date(2020, 1, 1),
                'address_line1': self.fake.street_address(),
                'city': self.fake.city(),
                'county': 'Dublin',
                'nationality': 'Irish',
                'country_code': 'IE'
            }
        )
        
        # Generate Fixed Assets
        self.generate_fixed_assets()
        
        # Generate Bank Reconciliation
        self.generate_bank_reconciliation()
        
        # Generate Dividends
        self.generate_dividends()
        
        self.stdout.write(self.style.SUCCESS("Accounting data generation complete!"))

    def generate_fixed_assets(self):
        self.stdout.write("Generating Fixed Assets...")
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        # Get asset accounts
        try:
            fa_account = Account.objects.get(code='1210', company=self.company)
            dep_account = Account.objects.get(code='1290', company=self.company)
            exp_account = Account.objects.get(code='5290', company=self.company)
        except Account.DoesNotExist:
            return
        
        # Create sample fixed assets
        assets_data = [
            ('LAPTOP-001', 'Dell Laptop XPS 15', date(2024, 1, 15), Decimal('1500.00'), Decimal('10.00'), Decimal('15.00')),
            ('DESK-001', 'Standing Desk - Electric', date(2024, 3, 20), Decimal('800.00'), Decimal('50.00'), Decimal('10.00')),
            ('CHAIR-001', 'Ergonomic Office Chair', date(2024, 3, 20), Decimal('450.00'), Decimal('25.00'), Decimal('10.00')),
            ('SERVER-001', 'Dell PowerEdge Server', date(2023, 6, 1), Decimal('5000.00'), Decimal('500.00'), Decimal('20.00')),
            ('PRINTER-001', 'HP LaserJet Pro', date(2024, 2, 10), Decimal('600.00'), Decimal('50.00'), Decimal('15.00')),
            ('VEHICLE-001', 'Company Van - Ford Transit', date(2023, 1, 1), Decimal('25000.00'), Decimal('5000.00'), Decimal('20.00')),
        ]
        
        for asset_code, name, purchase_date, purchase_value, salvage_value, dep_rate in assets_data:
            FixedAsset.objects.get_or_create(
                asset_code=asset_code,
                defaults={
                    'name': name,
                    'company': self.company,
                    'asset_account': fa_account,
                    'accumulated_depreciation_account': dep_account,
                    'depreciation_expense_account': exp_account,
                    'purchase_date': purchase_date,
                    'purchase_value': purchase_value,
                    'salvage_value': salvage_value,
                    'depreciation_method': 'SL',
                    'depreciation_rate': dep_rate,
                }
            )

    def generate_bank_reconciliation(self):
        self.stdout.write("Generating Bank Reconciliation...")
        from datetime import date
        from dateutil.relativedelta import relativedelta
        import calendar
        
        # Get bank account
        try:
            bank_account = Account.objects.get(code='1110', company=self.company)
        except Account.DoesNotExist:
            return
        
        # Generate 12 months of reconciliation
        opening_balance = Decimal('10000.00')
        for i in range(12):
            month_date = date.today() - relativedelta(months=11-i)
            last_day = calendar.monthrange(month_date.year, month_date.month)[1]
            period_date = date(month_date.year, month_date.month, last_day)
            
            # Random balance fluctuation
            closing_balance = opening_balance + Decimal(random.uniform(-2000, 5000))
            
            BankReconciliation.objects.get_or_create(
                company=self.company,
                account=bank_account,
                period_date=period_date,
                defaults={
                    'opening_balance': opening_balance,
                    'actual_closing_balance': closing_balance,
                    'book_balance': closing_balance + Decimal(random.uniform(-100, 100)),
                    'status': 'RC' if i < 10 else ('IP' if i == 10 else 'NS'),
                }
            )
            
            opening_balance = closing_balance

    def generate_dividends(self):
        self.stdout.write("Generating Dividends...")
        from datetime import date
        
        # Create sample dividends
        dividend_data = [
            ('John Doe', date(2024, 6, 30), date(2024, 7, 15), Decimal('0.25'), 10000),
            ('Jane Smith', date(2024, 6, 30), date(2024, 7, 15), Decimal('0.25'), 5000),
            ('Acme Holdings Ltd', date(2024, 12, 15), date(2024, 12, 31), Decimal('0.50'), 20000),
        ]
        
        for shareholder, dec_date, pay_date, per_share, shares in dividend_data:
            net_amount = per_share * Decimal(shares) * Decimal('0.80')  # 80% after tax
            Dividend.objects.get_or_create(
                company=self.company,
                shareholder_name=shareholder,
                declaration_date=dec_date,
                payment_date=pay_date,
                defaults={
                    'dividend_per_share': per_share,
                    'number_of_shares': shares,
                    'net_amount': net_amount,
                    'tax_credit': per_share * Decimal(shares) * Decimal('0.20'),
                    'voucher_number': f'DIV-{shareholder[:3].upper()}-{date.today().year}',
                    'is_paid': True,
                }
            )
