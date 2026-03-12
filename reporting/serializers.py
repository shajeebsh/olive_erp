from rest_framework import serializers

from company.models import CompanyProfile

from .models import (
    Dashboard,
    DashboardWidget,
    ReportDefinition,
    ReportExecution,
    ReportPlugin,
    Schedule,
)


class ReportDefinitionSerializer(serializers.ModelSerializer):
    """Serializer for ReportDefinition model."""

    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = ReportDefinition
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_configuration(self, value):
        """Validate report configuration JSON."""
        # Add validation logic for report configuration
        return value

    def create(self, validated_data):
        """Create a new report definition."""
        # Set owner from request user
        validated_data["owner"] = self.context["request"].user
        validated_data["company"] = CompanyProfile.objects.get_for_request(
            self.context["request"]
        )
        return super().create(validated_data)


class DashboardSerializer(serializers.ModelSerializer):
    """Serializer for Dashboard model."""

    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)
    widget_count = serializers.IntegerField(source="widgets.count", read_only=True)

    class Meta:
        model = Dashboard
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Serializer for DashboardWidget model."""

    report_definition_name = serializers.CharField(
        source="report_definition.name", read_only=True
    )

    class Meta:
        model = DashboardWidget
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer for Schedule model."""

    report_definition_name = serializers.CharField(
        source="report_definition.name", read_only=True
    )
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)

    class Meta:
        model = Schedule
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_cron_expression(self, value):
        """Validate cron expression if provided."""
        if value:
            # Add cron validation logic
            pass
        return value


class ReportExecutionSerializer(serializers.ModelSerializer):
    """Serializer for ReportExecution model."""

    report_definition_name = serializers.CharField(
        source="report_definition.name", read_only=True
    )
    executed_by_name = serializers.CharField(
        source="executed_by.get_full_name", read_only=True
    )

    class Meta:
        model = ReportExecution
        fields = "__all__"
        read_only_fields = ("id", "created_at", "started_at", "completed_at")


class ReportPluginSerializer(serializers.ModelSerializer):
    """Serializer for ReportPlugin model."""

    class Meta:
        model = ReportPlugin
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ReportGenerationRequestSerializer(serializers.Serializer):
    """Serializer for report generation requests."""

    parameters = serializers.JSONField(required=False, default=dict)
    force_refresh = serializers.BooleanField(default=False)
    export_format = serializers.ChoiceField(
        choices=["csv", "excel", "pdf", "json"], required=False
    )


class DashboardDataRequestSerializer(serializers.Serializer):
    """Serializer for dashboard data requests."""

    parameters = serializers.JSONField(required=False, default=dict)
    refresh_cache = serializers.BooleanField(default=False)


class ReportDefinitionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ReportDefinition with initial configuration."""

    class Meta:
        model = ReportDefinition
        fields = [
            "name",
            "description",
            "report_type",
            "data_source",
            "configuration",
            "filters",
            "columns",
        ]

    def create(self, validated_data):
        """Create report definition with default values."""
        validated_data["owner"] = self.context["request"].user
        validated_data["company"] = CompanyProfile.objects.get_for_request(
            self.context["request"]
        )
        return super().create(validated_data)


class ScheduleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Schedule with validation."""

    class Meta:
        model = Schedule
        fields = [
            "name",
            "report_definition",
            "frequency",
            "output_format",
            "cron_expression",
            "start_date",
            "end_date",
            "email_recipients",
            "email_subject",
            "email_message",
        ]

    def validate(self, attrs):
        """Validate schedule configuration."""
        if attrs["frequency"] == "CUSTOM" and not attrs.get("cron_expression"):
            raise serializers.ValidationError(
                "Cron expression is required for custom frequency"
            )
        return attrs
