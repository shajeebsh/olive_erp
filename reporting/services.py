import json
import time
import pandas as pd
from django.core.cache import cache
from django.db import connection
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db.models import Q
from celery import shared_task
from .models import ReportDefinition, ReportExecution, Schedule
from finance.models import Account, JournalEntry, Invoice
from inventory.models import Product, StockLevel, StockMovement
from hr.models import Employee, Leave, Attendance
from crm.models import Customer, SalesOrder
from projects.models import Project, Task
from purchasing.models import Supplier, PurchaseOrder
import logging

logger = logging.getLogger(__name__)


class ReportService:
    """
    Core service for report generation and data processing.
    Handles data retrieval, transformation, and caching.
    """
    
    def __init__(self, report_definition):
        self.report_definition = report_definition
        self.cache_key = f"report_{report_definition.id}"
    
    def generate_report(self, parameters=None, force_refresh=False):
        """
        Generate a report with optional parameters.
        Returns a ReportExecution instance with results.
        """
        execution = ReportExecution.objects.create(
            report_definition=self.report_definition,
            parameters=parameters or {},
            status=ReportExecution.ExecutionStatus.RUNNING
        )
        
        try:
            start_time = time.time()
            
            # Check cache first
            cached_data = self._get_cached_data()
            if cached_data and not force_refresh:
                execution.result_data = cached_data
                execution.status = ReportExecution.ExecutionStatus.COMPLETED
                execution.execution_time = timezone.timedelta(seconds=time.time() - start_time)
                execution.save()
                return execution
            
            # Generate fresh data
            data = self._retrieve_data(parameters)
            transformed_data = self._transform_data(data, parameters)
            
            # Cache the results
            self._cache_data(transformed_data)
            
            execution.result_data = transformed_data
            execution.status = ReportExecution.ExecutionStatus.COMPLETED
            execution.execution_time = timezone.timedelta(seconds=time.time() - start_time)
            execution.row_count = len(transformed_data.get('data', []))
            execution.save()
            
            return execution
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}", exc_info=True)
            execution.status = ReportExecution.ExecutionStatus.FAILED
            execution.error_message = str(e)
            execution.save()
            raise
    
    def _get_cached_data(self):
        """Retrieve cached report data."""
        return cache.get(self.cache_key)
    
    def _cache_data(self, data):
        """Cache report data with configured duration."""
        cache.set(self.cache_key, data, self.report_definition.cache_duration)
    
    def _retrieve_data(self, parameters):
        """Retrieve data based on report configuration."""
        data_source = self.report_definition.data_source
        
        if data_source == ReportDefinition.DataSource.FINANCE:
            return self._retrieve_finance_data(parameters)
        elif data_source == ReportDefinition.DataSource.INVENTORY:
            return self._retrieve_inventory_data(parameters)
        elif data_source == ReportDefinition.DataSource.HR:
            return self._retrieve_hr_data(parameters)
        elif data_source == ReportDefinition.DataSource.CRM:
            return self._retrieve_crm_data(parameters)
        elif data_source == ReportDefinition.DataSource.PROJECTS:
            return self._retrieve_projects_data(parameters)
        elif data_source == ReportDefinition.DataSource.PURCHASING:
            return self._retrieve_purchasing_data(parameters)
        else:
            raise ValueError(f"Unknown data source: {data_source}")
    
    def _retrieve_finance_data(self, parameters):
        """Retrieve finance data for reports."""
        filters = Q(company=self.report_definition.company)
        
        # Apply date filters if specified
        if parameters.get('start_date') and parameters.get('end_date'):
            filters &= Q(date__range=[parameters['start_date'], parameters['end_date']])
        
        data = {
            'accounts': list(Account.objects.filter(filters).values()),
            'journal_entries': list(JournalEntry.objects.filter(filters).values()),
            'invoices': list(Invoice.objects.filter(filters).values()),
        }
        
        return data
    
    def _retrieve_inventory_data(self, parameters):
        """Retrieve inventory data for reports."""
        filters = Q()
        
        if parameters.get('warehouse_id'):
            filters &= Q(warehouse_id=parameters['warehouse_id'])
        
        data = {
            'products': list(Product.objects.filter(company=self.report_definition.company).values()),
            'stock_levels': list(StockLevel.objects.filter(filters).values()),
            'stock_movements': list(StockMovement.objects.filter(filters).values()),
        }
        
        return data
    
    def _retrieve_hr_data(self, parameters):
        """Retrieve HR data for reports."""
        filters = Q(company=self.report_definition.company)
        
        if parameters.get('department_id'):
            filters &= Q(department_id=parameters['department_id'])
        
        data = {
            'employees': list(Employee.objects.filter(filters).values()),
            'leaves': list(Leave.objects.filter(filters).values()),
            'attendances': list(Attendance.objects.filter(filters).values()),
        }
        
        return data
    
    def _retrieve_crm_data(self, parameters):
        """Retrieve CRM data for reports."""
        filters = Q(company=self.report_definition.company)
        
        if parameters.get('customer_status'):
            filters &= Q(status=parameters['customer_status'])
        
        data = {
            'customers': list(Customer.objects.filter(filters).values()),
            'sales_orders': list(SalesOrder.objects.filter(filters).values()),
        }
        
        return data
    
    def _retrieve_projects_data(self, parameters):
        """Retrieve projects data for reports."""
        filters = Q(company=self.report_definition.company)
        
        if parameters.get('project_status'):
            filters &= Q(status=parameters['project_status'])
        
        data = {
            'projects': list(Project.objects.filter(filters).values()),
            'tasks': list(Task.objects.filter(filters).values()),
        }
        
        return data
    
    def _retrieve_purchasing_data(self, parameters):
        """Retrieve purchasing data for reports."""
        filters = Q(company=self.report_definition.company)
        
        if parameters.get('supplier_id'):
            filters &= Q(supplier_id=parameters['supplier_id'])
        
        data = {
            'suppliers': list(Supplier.objects.filter(filters).values()),
            'purchase_orders': list(PurchaseOrder.objects.filter(filters).values()),
        }
        
        return data
    
    def _transform_data(self, data, parameters):
        """Transform raw data based on report configuration."""
        config = self.report_definition.configuration
        
        # Apply transformations based on report type
        if self.report_definition.report_type == ReportDefinition.ReportType.PIVOT:
            return self._create_pivot_table(data, config)
        elif self.report_definition.report_type == ReportDefinition.ReportType.CHART:
            return self._prepare_chart_data(data, config)
        else:
            return self._prepare_table_data(data, config)
    
    def _create_pivot_table(self, data, config):
        """Create pivot table from data."""
        # Implementation for pivot tables
        return data
    
    def _prepare_chart_data(self, data, config):
        """Prepare data for chart visualization."""
        # Implementation for chart data preparation
        return data
    
    def _prepare_table_data(self, data, config):
        """Prepare data for table display."""
        # Implementation for table data preparation
        return data


class ExportService:
    """
    Service for exporting reports to various formats.
    """
    
    @staticmethod
    def export_to_csv(execution, filename=None):
        """Export report data to CSV format."""
        data = execution.result_data
        df = pd.DataFrame(data.get('data', []))
        
        csv_content = df.to_csv(index=False)
        filename = filename or f"report_{execution.id}.csv"
        
        execution.output_file.save(filename, ContentFile(csv_content))
        execution.save()
        
        return execution
    
    @staticmethod
    def export_to_excel(execution, filename=None):
        """Export report data to Excel format."""
        data = execution.result_data
        df = pd.DataFrame(data.get('data', []))
        
        excel_content = df.to_excel(index=False)
        filename = filename or f"report_{execution.id}.xlsx"
        
        execution.output_file.save(filename, ContentFile(excel_content))
        execution.save()
        
        return execution
    
    @staticmethod
    def export_to_pdf(execution, filename=None):
        """Export report data to PDF format."""
        # PDF generation implementation would go here
        # This would typically use a library like WeasyPrint or ReportLab
        pass


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_scheduled_report_task(self, schedule_id, parameters=None):
    """
    Celery task for generating scheduled reports.
    """
    try:
        schedule = Schedule.objects.get(id=schedule_id)
        report_service = ReportService(schedule.report_definition)
        
        execution = report_service.generate_report(parameters)
        
        # Export based on schedule configuration
        if schedule.output_format == Schedule.OutputFormat.CSV:
            ExportService.export_to_csv(execution)
        elif schedule.output_format == Schedule.OutputFormat.EXCEL:
            ExportService.export_to_excel(execution)
        elif schedule.output_format == Schedule.OutputFormat.PDF:
            ExportService.export_to_pdf(execution)
        
        # Send email if configured
        if schedule.email_recipients:
            send_report_email.delay(execution.id, schedule.email_recipients)
        
        return str(execution.id)
        
    except Exception as exc:
        logger.error(f"Scheduled report generation failed: {exc}")
        raise self.retry(exc=exc)


@shared_task
def send_report_email(execution_id, recipients):
    """
    Celery task for sending report emails.
    """
    # Email sending implementation would go here
    pass


class DashboardService:
    """
    Service for dashboard operations and widget management.
    """
    
    @staticmethod
    def get_dashboard_data(dashboard, parameters=None):
        """
        Get data for all widgets in a dashboard.
        """
        dashboard_data = []
        
        for widget in dashboard.widgets.all():
            report_service = ReportService(widget.report_definition)
            execution = report_service.generate_report(parameters)
            
            dashboard_data.append({
                'widget_id': str(widget.id),
                'title': widget.title,
                'data': execution.result_data,
                'config': widget.config
            })
        
        return dashboard_data


class CacheService:
    """
    Service for managing report caching strategies.
    """
    
    @staticmethod
    def clear_report_cache(report_definition_id):
        """Clear cache for a specific report."""
        cache_key = f"report_{report_definition_id}"
        cache.delete(cache_key)
    
    @staticmethod
    def clear_all_reports_cache():
        """Clear cache for all reports."""
        # This would need a more sophisticated approach in production
        # Possibly using Redis patterns or a dedicated cache namespace
        pass