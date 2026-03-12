from django.apps import AppConfig


class ReportingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reporting'
    verbose_name = 'Reporting & BI'
    
    def ready(self):
        # Import signals to ensure they are registered
        import reporting.signals