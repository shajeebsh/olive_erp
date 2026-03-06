from wagtail.snippets.models import register_snippet
from crm.models import Customer
from purchasing.models import Supplier
from inventory.models import Product
from hr.models import Employee

register_snippet(Customer)
register_snippet(Supplier)
register_snippet(Product)
register_snippet(Employee)
