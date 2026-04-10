import os
import json
from django.urls import path
from django.contrib import messages
from django.shortcuts import render
from django.core.management import call_command
from django.conf import settings
from django.http import JsonResponse
from wagtail import hooks
from wagtail.snippets.models import register_snippet
from crm.models import Customer
from purchasing.models import Supplier
from inventory.models import Product
from hr.models import Employee
import threading

register_snippet(Customer)
register_snippet(Supplier)
register_snippet(Product)
register_snippet(Employee)

STATUS_FILE = os.path.join(settings.MEDIA_ROOT, 'sample_data_status.txt')
LOG_FILE = os.path.join(settings.MEDIA_ROOT, 'sample_data_log.json')

def write_status(status):
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    with open(STATUS_FILE, 'w') as f:
        f.write(status)

def read_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            return f.read().strip()
    return ''

def read_log():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def clear_log():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('system/sample-data/', sample_data_view, name='sample_data'),
        path('system/sample-data/log/', sample_data_log_view, name='sample_data_log'),
        path('system/data-profiling/', data_profiling_view, name='data_profiling'),
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


@hooks.register('register_admin_menu_item')
def register_data_profiling_menu_item():
    from wagtail.admin.menu import MenuItem
    return MenuItem(
        'Data Profiling',
        '/admin/system/data-profiling/',
        icon_name='dashboard',
        order=101,
    )


def sample_data_log_view(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    logs = read_log()
    status = read_status()
    return JsonResponse({'logs': logs, 'status': status})


def sample_data_view(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'wagtailadmin/sample_data.html', {})

    status = read_status()
    logs = read_log()
    
    if status.startswith('ERROR:'):
        messages.error(request, status.replace('ERROR:', '').strip())
        write_status('')
    elif status == 'IN_PROGRESS':
        messages.info(request, 'Sample data generation is currently in progress.')
    elif status == 'COMPLETE':
        messages.success(request, 'Sample data generation completed successfully.')
        write_status('')

    if request.method == 'POST':
        clear_existing = request.POST.get('clear_existing') == 'on'
        
        write_status('IN_PROGRESS')
        clear_log()
        
        def run_sample_data():
            try:
                call_command('generate_sample_data', num_months=6, clear_existing=clear_existing)
                write_status('COMPLETE')
            except Exception as e:
                write_status(f'ERROR: {str(e)}')

        thread = threading.Thread(target=run_sample_data)
        thread.start()

        messages.success(request, 'Sample data generation has started in the background. This may take a few minutes.')
        return render(request, 'wagtailadmin/sample_data.html', {})

    return render(request, 'wagtailadmin/sample_data.html', {'logs': logs, 'status': status})


def data_profiling_view(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'wagtailadmin/profiling.html', {})

    from django.apps import apps
    
    selected_model = request.GET.get('model')
    deep_stats = None
    chart_data = None
    
    modules = {
        'Company': ['company.CompanyProfile', 'company.Currency'],
        'Finance': ['finance.Account', 'finance.Invoice', 'finance.JournalEntry', 'finance.Budget'],
        'Inventory': ['inventory.Product', 'inventory.Category', 'inventory.Warehouse', 'inventory.StockLevel'],
        'CRM': ['crm.Customer', 'crm.Lead', 'crm.SalesOrder'],
        'HR': ['hr.Employee', 'hr.Department', 'hr.LeaveRequest', 'hr.Attendance'],
        'Projects': ['projects.Project', 'projects.Task'],
        'Purchasing': ['purchasing.Supplier', 'purchasing.PurchaseOrder'],
        'Tax Engine': ['tax_engine.TaxPeriod', 'tax_engine.TaxFiling'],
        'Accounting': ['apps.accounting.assets.FixedAsset', 'apps.accounting.reconciliation.BankReconciliation'],
    }
    
    profile_data = {}
    total_count = 0
    
    for module_name, model_paths in modules.items():
        module_counts = {}
        for model_path in model_paths:
            try:
                app_label, model_name = model_path.split('.')
                model = apps.get_model(app_label, model_name)
                count = model.objects.count()
                module_counts[model_name] = count
                total_count += count
            except Exception:
                module_counts[model_name] = 'N/A'
        profile_data[module_name] = module_counts
    
    if selected_model:
        try:
            app_label, model_name = selected_model.split('.')
            model = apps.get_model(app_label, model_name)
            qs = model.objects.all()
            total_rows = qs.count()
            
            stats = []
            for field in model._meta.get_fields():
                if field.name == 'id':
                    continue
                field_name = field.name
                try:
                    null_count = qs.filter(**{f'{field_name}__isnull': True}).count()
                    filled_count = total_rows - null_count
                    null_pct = (null_count / total_rows * 100) if total_rows > 0 else 0
                    
                    distinct_count = qs.values(field_name).distinct().count() if filled_count > 0 else 0
                    
                    field_type = field.get_internal_type()
                    min_val = None
                    max_val = None
                    if field_type in ['DateField', 'DateTimeField', 'IntegerField', 'DecimalField', 'FloatField']:
                        try:
                            min_val = qs.exclude(**{f'{field_name}__isnull': True}).order_by(field_name).first()
                            max_val = qs.exclude(**{f'{field_name}__isnull': True}).order_by(f'-{field_name}').first()
                            if min_val:
                                min_val = getattr(min_val, field_name)
                            if max_val:
                                max_val = getattr(max_val, field_name)
                        except:
                            pass
                    
                    stats.append({
                        'column': field_name,
                        'type': field_type,
                        'null_count': null_count,
                        'filled_count': filled_count,
                        'null_percentage': round(null_pct, 2),
                        'distinct_count': distinct_count,
                        'min': str(min_val) if min_val else 'N/A',
                        'max': str(max_val) if max_val else 'N/A',
                    })
                except Exception as e:
                    stats.append({'column': field_name, 'type': 'unknown', 'error': str(e)})
            
            deep_stats = {
                'model': selected_model,
                'total_rows': total_rows,
                'columns': stats,
            }
            
            null_count_total = sum(s.get('null_count', 0) for s in stats)
            filled_count_total = sum(s.get('filled_count', 0) for s in stats)
            chart_data = {
                'labels': ['Filled', 'Null/Empty'],
                'data': [filled_count_total, null_count_total],
            }
        except Exception as e:
            messages.error(request, f"Error analyzing model: {str(e)}")
    
    return render(request, 'wagtailadmin/profiling.html', {
        'profile_data': profile_data,
        'total_count': total_count,
        'selected_model': selected_model,
        'deep_stats': deep_stats,
        'chart_data': chart_data,
        'modules': modules,
    })