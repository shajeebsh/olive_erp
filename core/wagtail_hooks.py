import os
import json
import csv
from django.urls import path
from django.contrib import messages
from django.shortcuts import render
from django.core.management import call_command
from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from django.db.models.query import QuerySet
from wagtail import hooks
from wagtail.snippets.models import register_snippet
from crm.models import Customer
from purchasing.models import Supplier
from inventory.models import Product
from hr.models import Employee
from company.models import CompanyProfile, Currency
from tax_engine.models import TaxPeriod
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
        path('system/data-profiling/export/', export_model_csv, name='data_profiling_export'),
        path('system/readiness/', system_readiness_view, name='system_readiness'),
    ]


@hooks.register('register_admin_menu_section')
def register_system_tools_section():
    from wagtail.admin.menu import MenuSection
    return MenuSection(
        name='system_tools',
        title='System Tools',
        icon='cog',
        order=50,
    )


@hooks.register('register_admin_menu_item')
def register_system_tools_menu_items(request):
    from wagtail.admin.menu import MenuItem, SubmenuMenuItem
    from wagtail.admin.collections import CollectionMenu
    from wagtail.core.models import Collection
    
    items = [
        MenuItem('Readiness Check', '/admin/system/readiness/', icon_name='check', order=0),
        MenuItem('Sample Data', '/admin/system/sample-data/', icon_name='snippet', order=1),
        MenuItem('Data Profiling', '/admin/system/data-profiling/', icon_name='dashboard', order=2),
    ]
    
    return SubmenuMenuItem('System Tools', items, icon_name='cog', order=50)


def export_model_csv(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    model_path = request.GET.get('model')
    if not model_path:
        return JsonResponse({'error': 'model parameter required'}, status=400)
    
    try:
        app_label, model_name = model_path.split('.')
        from django.apps import apps
        model = apps.get_model(app_label, model_name)
    except Exception as e:
        return JsonResponse({'error': f'Invalid model: {str(e)}'}, status=400)
    
    class Echo:
        def write(self, value):
            return value

    def generate_rows():
        # Header
        fields = [f.name for f in model._meta.get_fields() if f.name != 'id']
        yield ','.join(fields) + '\n'
        
        # Data rows
        for obj in model.objects.all().iterator():
            row = []
            for field_name in fields:
                try:
                    val = getattr(obj, field_name)
                    if val is None:
                        row.append('')
                    else:
                        row.append(str(val).replace(',', ';'))
                except:
                    row.append('')
            yield ','.join(row) + '\n'
    
    response = StreamingHttpResponse(generate_rows(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{model_name}.csv"'
    return response


def system_readiness_view(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'wagtailadmin/readiness.html', {})
    
    from django.apps import apps
    
    # Check Company Profile
    company_profile = CompanyProfile.objects.first()
    company_status = 'set' if company_profile else 'not_set'
    
    # Check Currency
    currency_count = Currency.objects.count()
    currency_status = 'set' if currency_count > 0 else 'empty'
    
    # Check Tax Period
    tax_period = TaxPeriod.objects.filter(is_active=True).first()
    tax_period_status = 'set' if tax_period else 'not_set'
    
    # Module record counts
    modules = {
        'Finance': ['finance.Account', 'finance.Invoice', 'finance.JournalEntry'],
        'Inventory': ['inventory.Product', 'inventory.Warehouse'],
        'CRM': ['crm.Customer', 'crm.Lead'],
        'HR': ['hr.Employee', 'hr.Department'],
        'Projects': ['projects.Project'],
        'Purchasing': ['purchasing.Supplier'],
    }
    
    record_checks = []
    for module_name, model_paths in modules.items():
        total = 0
        for model_path in model_paths:
            try:
                app_label, model_name = model_path.split('.')
                model = apps.get_model(app_label, model_name)
                total += model.objects.count()
            except:
                pass
        record_checks.append({
            'module': module_name,
            'count': total,
            'status': 'green' if total > 0 else 'red'
        })
    
    readiness_data = {
        'company': {'status': company_status, 'value': str(company_profile) if company_profile else 'Not configured'},
        'currency': {'status': currency_status, 'value': f'{currency_count} currencies'},
        'tax_period': {'status': tax_period_status, 'value': str(tax_period) if tax_period else 'No active period'},
        'records': record_checks,
    }
    
    return render(request, 'wagtailadmin/readiness.html', {'readiness': readiness_data})


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
    null_bar_chart = None
    row_preview = None
    active_tab = request.GET.get('tab', 'columns')
    
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
        module_total = 0
        for model_path in model_paths:
            try:
                app_label, model_name = model_path.split('.')
                model = apps.get_model(app_label, model_name)
                count = model.objects.count()
                module_counts[model_name] = count
                module_total += count
            except Exception:
                module_counts[model_name] = 'N/A'
        profile_data[module_name] = {
            'models': module_counts,
            'total': module_total
        }
        total_count += module_total
    
    if selected_model:
        try:
            app_label, model_name = selected_model.split('.')
            model = apps.get_model(app_label, model_name)
            qs = model.objects.all()
            total_rows = qs.count()
            
            # Row preview - first 50 records
            row_preview = list(qs[:50].values())[:50]
            
            stats = []
            null_bar_labels = []
            null_bar_data = []
            
            from django.db.models import Min, Max
            
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
                            agg = qs.aggregate(min_val=Min(field_name), max_val=Max(field_name))
                            min_val = agg.get('min_val')
                            max_val = agg.get('max_val')
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
                    
                    null_bar_labels.append(field_name)
                    null_bar_data.append(round(null_pct, 1))
                    
                except Exception as e:
                    stats.append({'column': field_name, 'type': 'unknown', 'error': str(e)})
                    null_bar_labels.append(field_name)
                    null_bar_data.append(0)
            
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
            
            null_bar_chart = {
                'labels': null_bar_labels,
                'data': null_bar_data,
            }
        except Exception as e:
            messages.error(request, f"Error analyzing model: {str(e)}")
    
    return render(request, 'wagtailadmin/profiling.html', {
        'profile_data': profile_data,
        'total_count': total_count,
        'selected_model': selected_model,
        'deep_stats': deep_stats,
        'chart_data': chart_data,
        'null_bar_chart': null_bar_chart,
        'row_preview': row_preview,
        'active_tab': active_tab,
        'modules': modules,
    })