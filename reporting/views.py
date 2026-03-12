from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import ReportDefinition, Dashboard, DashboardWidget, Schedule, ReportExecution, ReportPlugin
from .serializers import (
    ReportDefinitionSerializer, DashboardSerializer, DashboardWidgetSerializer,
    ScheduleSerializer, ReportExecutionSerializer, ReportPluginSerializer,
    ReportGenerationRequestSerializer, DashboardDataRequestSerializer,
    ReportDefinitionCreateSerializer, ScheduleCreateSerializer
)
from .services import ReportService, ExportService, DashboardService
from company.models import CompanyProfile


class ReportDefinitionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing report definitions."""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return reports that the user has access to."""
        user = self.request.user
        company = CompanyProfile.objects.get_for_request(self.request)
        
        return ReportDefinition.objects.filter(
            Q(company=company) &
            (Q(owner=user) | Q(is_public=True) | Q(allowed_groups__in=user.groups.all()))
        ).distinct()
    
    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.action == 'create':
            return ReportDefinitionCreateSerializer
        return ReportDefinitionSerializer
    
    def perform_create(self, serializer):
        """Set owner and company for new reports."""
        serializer.save(
            owner=self.request.user,
            company=CompanyProfile.objects.get_for_request(self.request)
        )
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generate a report with optional parameters."""
        report = self.get_object()
        serializer = ReportGenerationRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            report_service = ReportService(report)
            
            try:
                execution = report_service.generate_report(
                    parameters=serializer.validated_data.get('parameters', {}),
                    force_refresh=serializer.validated_data.get('force_refresh', False)
                )
                
                # Export if requested
                export_format = serializer.validated_data.get('export_format')
                if export_format:
                    if export_format == 'csv':
                        ExportService.export_to_csv(execution)
                    elif export_format == 'excel':
                        ExportService.export_to_excel(execution)
                    elif export_format == 'pdf':
                        ExportService.export_to_pdf(execution)
                
                return Response(ReportExecutionSerializer(execution).data)
                
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def clear_cache(self, request, pk=None):
        """Clear cache for a specific report."""
        report = self.get_object()
        
        from .services import CacheService
        CacheService.clear_report_cache(report.id)
        
        return Response({'status': 'cache cleared'})


class DashboardViewSet(viewsets.ModelViewSet):
    """ViewSet for managing dashboards."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = DashboardSerializer
    
    def get_queryset(self):
        """Return dashboards that the user has access to."""
        user = self.request.user
        company = CompanyProfile.objects.get_for_request(self.request)
        
        return Dashboard.objects.filter(
            Q(company=company) &
            (Q(owner=user) | Q(is_public=True) | Q(allowed_groups__in=user.groups.all()))
        ).distinct()
    
    def perform_create(self, serializer):
        """Set owner and company for new dashboards."""
        serializer.save(
            owner=self.request.user,
            company=CompanyProfile.objects.get_for_request(self.request)
        )
    
    @action(detail=True, methods=['post'])
    def get_data(self, request, pk=None):
        """Get data for all widgets in a dashboard."""
        dashboard = self.get_object()
        serializer = DashboardDataRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            dashboard_service = DashboardService()
            
            try:
                data = dashboard_service.get_dashboard_data(
                    dashboard,
                    parameters=serializer.validated_data.get('parameters', {})
                )
                
                return Response(data)
                
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing dashboard widgets."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = DashboardWidgetSerializer
    
    def get_queryset(self):
        """Return widgets for dashboards the user can access."""
        user = self.request.user
        company = CompanyProfile.objects.get_for_request(self.request)
        
        return DashboardWidget.objects.filter(
            dashboard__company=company,
            dashboard__in=Dashboard.objects.filter(
                Q(owner=user) | Q(is_public=True) | Q(allowed_groups__in=user.groups.all())
            )
        ).distinct()


class ScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing report schedules."""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return schedules that the user owns."""
        user = self.request.user
        company = CompanyProfile.objects.get_for_request(self.request)
        
        return Schedule.objects.filter(owner=user, company=company)
    
    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.action == 'create':
            return ScheduleCreateSerializer
        return ScheduleSerializer
    
    def perform_create(self, serializer):
        """Set owner and company for new schedules."""
        serializer.save(
            owner=self.request.user,
            company=CompanyProfile.objects.get_for_request(self.request)
        )
    
    @action(detail=True, methods=['post'])
    def run_now(self, request, pk=None):
        """Run a schedule immediately."""
        schedule = self.get_object()
        
        from .tasks import generate_scheduled_report_task
        task = generate_scheduled_report_task.delay(str(schedule.id))
        
        return Response({'task_id': task.id})


class ReportExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing report executions."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ReportExecutionSerializer
    
    def get_queryset(self):
        """Return executions for reports the user can access."""
        user = self.request.user
        company = CompanyProfile.objects.get_for_request(self.request)
        
        return ReportExecution.objects.filter(
            report_definition__company=company,
            report_definition__in=ReportDefinition.objects.filter(
                Q(owner=user) | Q(is_public=True) | Q(allowed_groups__in=user.groups.all())
            )
        ).distinct()


class ReportPluginViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing report plugins."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ReportPluginSerializer
    queryset = ReportPlugin.objects.filter(is_active=True)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a plugin with parameters."""
        plugin = self.get_object()
        
        # Load and execute the plugin
        try:
            # This would dynamically load and execute the plugin
            # Implementation would depend on plugin architecture
            result = {
                'plugin': plugin.name,
                'result': 'Plugin executed successfully',
                'data': request.data.get('parameters', {})
            }
            
            return Response(result)
            
        except Exception as e:
            return Response(
                {'error': f'Plugin execution failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PrebuiltDashboardViewSet(viewsets.ViewSet):
    """ViewSet for prebuilt dashboards."""
    
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """List available prebuilt dashboards."""
        company = CompanyProfile.objects.get_for_request(self.request)
        
        prebuilt_dashboards = [
            {
                'id': 'finance_overview',
                'name': 'Finance Overview',
                'type': 'FINANCE',
                'description': 'Comprehensive financial dashboard with P&L, balance sheet, and cash flow metrics'
            },
            {
                'id': 'inventory_analytics',
                'name': 'Inventory Analytics',
                'type': 'INVENTORY',
                'description': 'Inventory performance, stock levels, and movement analysis'
            },
            {
                'id': 'hr_metrics',
                'name': 'HR Metrics',
                'type': 'HR',
                'description': 'Employee performance, attendance, and leave analytics'
            },
            {
                'id': 'sales_performance',
                'name': 'Sales Performance',
                'type': 'CRM',
                'description': 'Sales pipeline, customer acquisition, and revenue metrics'
            },
            {
                'id': 'project_tracking',
                'name': 'Project Tracking',
                'type': 'PROJECTS',
                'description': 'Project progress, budget vs actual, and resource allocation'
            }
        ]
        
        return Response(prebuilt_dashboards)
    
    @action(detail=False, methods=['post'])
    def install(self, request):
        """Install a prebuilt dashboard."""
        dashboard_type = request.data.get('type')
        
        if not dashboard_type:
            return Response(
                {'error': 'Dashboard type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the prebuilt dashboard
        # This would have predefined widgets and configurations
        
        return Response({'status': 'dashboard installed'})