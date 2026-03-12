from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from company.models import CompanyProfile
import uuid


class ReportDefinition(models.Model):
    """
    Defines a report with its configuration, filters, and layout.
    Supports drag-drop interface for building reports.
    """
    
    class ReportType(models.TextChoices):
        TABLE = 'TABLE', _('Table')
        CHART = 'CHART', _('Chart')
        PIVOT = 'PIVOT', _('Pivot Table')
        SUMMARY = 'SUMMARY', _('Summary')
        CUSTOM = 'CUSTOM', _('Custom')
    
    class DataSource(models.TextChoices):
        FINANCE = 'FINANCE', _('Finance')
        INVENTORY = 'INVENTORY', _('Inventory')
        HR = 'HR', _('Human Resources')
        CRM = 'CRM', _('CRM')
        PROJECTS = 'PROJECTS', _('Projects')
        PURCHASING = 'PURCHASING', _('Purchasing')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("report name"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    report_type = models.CharField(_("report type"), max_length=20, choices=ReportType.choices)
    data_source = models.CharField(_("data source"), max_length=20, choices=DataSource.choices)
    
    # Report configuration (JSON field for flexible schema)
    configuration = JSONField(_("report configuration"), default=dict)
    filters = JSONField(_("report filters"), default=dict)
    columns = JSONField(_("report columns"), default=list)
    
    # Ownership and permissions
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    is_public = models.BooleanField(_("is public"), default=False)
    
    # Groups that can access this report
    allowed_groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_("allowed groups"),
        blank=True,
        help_text=_("Groups that can access this report")
    )
    
    # Performance and caching
    cache_duration = models.IntegerField(_("cache duration (seconds)"), default=300)
    is_active = models.BooleanField(_("is active"), default=True)
    
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    
    class Meta:
        verbose_name = _("Report Definition")
        verbose_name_plural = _("Report Definitions")
        ordering = ['name']
        indexes = [
            models.Index(fields=['report_type', 'data_source']),
            models.Index(fields=['is_active', 'is_public']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class Dashboard(models.Model):
    """
    Prebuilt or custom dashboard containing multiple report widgets.
    """
    
    class DashboardType(models.TextChoices):
        FINANCE = 'FINANCE', _('Finance Dashboard')
        INVENTORY = 'INVENTORY', _('Inventory Dashboard')
        HR = 'HR', _('HR Dashboard')
        CRM = 'CRM', _('CRM Dashboard')
        PROJECTS = 'PROJECTS', _('Projects Dashboard')
        CUSTOM = 'CUSTOM', _('Custom Dashboard')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("dashboard name"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    dashboard_type = models.CharField(_("dashboard type"), max_length=20, choices=DashboardType.choices)
    
    # Layout configuration (grid layout with widget positions)
    layout_config = JSONField(_("layout configuration"), default=dict)
    
    # Ownership and permissions
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dashboards')
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    is_public = models.BooleanField(_("is public"), default=False)
    
    # Groups that can access this dashboard
    allowed_groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_("allowed groups"),
        blank=True,
        help_text=_("Groups that can access this dashboard")
    )
    
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    
    class Meta:
        verbose_name = _("Dashboard")
        verbose_name_plural = _("Dashboards")
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_dashboard_type_display()})"


class DashboardWidget(models.Model):
    """
    Individual widget on a dashboard, referencing a report definition.
    """
    
    class WidgetType(models.TextChoices):
        CHART = 'CHART', _('Chart')
        TABLE = 'TABLE', _('Table')
        METRIC = 'METRIC', _('Metric')
        PIVOT = 'PIVOT', _('Pivot Table')
        CUSTOM = 'CUSTOM', _('Custom')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='widgets')
    report_definition = models.ForeignKey(ReportDefinition, on_delete=models.CASCADE)
    
    widget_type = models.CharField(_("widget type"), max_length=20, choices=WidgetType.choices)
    title = models.CharField(_("widget title"), max_length=255)
    
    # Widget position and size in the dashboard grid
    position_x = models.IntegerField(_("position X"), default=0)
    position_y = models.IntegerField(_("position Y"), default=0)
    width = models.IntegerField(_("width"), default=4, validators=[MinValueValidator(1), MaxValueValidator(12)])
    height = models.IntegerField(_("height"), default=4, validators=[MinValueValidator(1), MaxValueValidator(12)])
    
    # Widget-specific configuration
    config = JSONField(_("widget configuration"), default=dict)
    
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    
    class Meta:
        verbose_name = _("Dashboard Widget")
        verbose_name_plural = _("Dashboard Widgets")
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        return f"{self.title} - {self.dashboard.name}"


class Schedule(models.Model):
    """
    Schedule configuration for automated report generation and distribution.
    """
    
    class ScheduleFrequency(models.TextChoices):
        DAILY = 'DAILY', _('Daily')
        WEEKLY = 'WEEKLY', _('Weekly')
        MONTHLY = 'MONTHLY', _('Monthly')
        QUARTERLY = 'QUARTERLY', _('Quarterly')
        YEARLY = 'YEARLY', _('Yearly')
        CUSTOM = 'CUSTOM', _('Custom')
    
    class OutputFormat(models.TextChoices):
        CSV = 'CSV', _('CSV')
        EXCEL = 'EXCEL', _('Excel')
        PDF = 'PDF', _('PDF')
        HTML = 'HTML', _('HTML')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("schedule name"), max_length=255)
    report_definition = models.ForeignKey(ReportDefinition, on_delete=models.CASCADE)
    
    frequency = models.CharField(_("frequency"), max_length=20, choices=ScheduleFrequency.choices)
    output_format = models.CharField(_("output format"), max_length=20, choices=OutputFormat.choices)
    
    # Schedule configuration
    cron_expression = models.CharField(_("cron expression"), max_length=100, blank=True)
    start_date = models.DateTimeField(_("start date"))
    end_date = models.DateTimeField(_("end date"), null=True, blank=True)
    
    # Email distribution
    email_recipients = models.TextField(_("email recipients"), help_text=_("Comma-separated list of email addresses"))
    email_subject = models.CharField(_("email subject"), max_length=255)
    email_message = models.TextField(_("email message"), blank=True)
    
    # Status and ownership
    is_active = models.BooleanField(_("is active"), default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    
    class Meta:
        verbose_name = _("Schedule")
        verbose_name_plural = _("Schedules")
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.report_definition.name}"


class ReportExecution(models.Model):
    """
    Tracks execution of reports, including performance metrics and results.
    """
    
    class ExecutionStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        RUNNING = 'RUNNING', _('Running')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')
        CANCELLED = 'CANCELLED', _('Cancelled')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_definition = models.ForeignKey(ReportDefinition, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(_("status"), max_length=20, choices=ExecutionStatus.choices, default=ExecutionStatus.PENDING)
    
    # Performance metrics
    execution_time = models.DurationField(_("execution time"), null=True, blank=True)
    row_count = models.IntegerField(_("row count"), null=True, blank=True)
    memory_usage = models.IntegerField(_("memory usage (KB)"), null=True, blank=True)
    
    # Results and output
    result_data = JSONField(_("result data"), null=True, blank=True)
    output_file = models.FileField(_("output file"), upload_to='reports/%Y/%m/%d/', null=True, blank=True)
    error_message = models.TextField(_("error message"), blank=True)
    
    # Execution context
    executed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    parameters = JSONField(_("execution parameters"), default=dict)
    
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    started_at = models.DateTimeField(_("started at"), null=True, blank=True)
    completed_at = models.DateTimeField(_("completed at"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Report Execution")
        verbose_name_plural = _("Report Executions")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['report_definition', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.report_definition.name} - {self.get_status_display()} - {self.created_at}"


class ReportPlugin(models.Model):
    """
    Plugin system for custom report types and data sources.
    """
    
    class PluginType(models.TextChoices):
        DATA_SOURCE = 'DATA_SOURCE', _('Data Source')
        VISUALIZATION = 'VISUALIZATION', _('Visualization')
        EXPORT = 'EXPORT', _('Export Format')
        TRANSFORMATION = 'TRANSFORMATION', _('Data Transformation')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("plugin name"), max_length=255)
    plugin_type = models.CharField(_("plugin type"), max_length=20, choices=PluginType.choices)
    
    # Plugin configuration
    module_path = models.CharField(_("module path"), max_length=500)
    config_schema = JSONField(_("configuration schema"), default=dict)
    
    # Metadata
    version = models.CharField(_("version"), max_length=20, default='1.0.0')
    is_active = models.BooleanField(_("is active"), default=True)
    author = models.CharField(_("author"), max_length=255, blank=True)
    description = models.TextField(_("description"), blank=True)
    
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    
    class Meta:
        verbose_name = _("Report Plugin")
        verbose_name_plural = _("Report Plugins")
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_plugin_type_display()})"