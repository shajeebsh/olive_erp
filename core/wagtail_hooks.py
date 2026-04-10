from django.urls import path
from django.contrib import messages
from django.shortcuts import render
from django.conf import settings
from wagtail import hooks
from wagtail.snippets.models import register_snippet
from crm.models import Customer
from purchasing.models import Supplier
from inventory.models import Product
from hr.models import Employee
from core.management.commands.generate_sample_data import Command as SampleDataCommand
import threading

register_snippet(Customer)
register_snippet(Supplier)
register_snippet(Product)
register_snippet(Employee)


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('system/sample-data/', sample_data_view, name='sample_data'),
    ]


@hooks.register('register_admin_menu_item')
def register_sample_data_menu_item():
    from wagtail.admin.menu import MenuItem
    return MenuItem(
        'Sample Data',
        '/admin/system/sample-data/',
        icon_name='snippet',
        order=100,
    )


def sample_data_view(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'wagtailadmin/sample_data.html', {})

    if request.method == 'POST':
        def run_sample_data():
            cmd = SampleDataCommand()
            cmd.handle(num_months=6)

        thread = threading.Thread(target=run_sample_data)
        thread.start()

        messages.success(request, 'Sample data generation has started in the background. This may take a few minutes.')
        return render(request, 'wagtailadmin/sample_data.html', {})

    return render(request, 'wagtailadmin/sample_data.html', {})