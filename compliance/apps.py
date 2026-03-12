from django.apps import AppConfig


class ComplianceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'compliance'
    verbose_name = 'Tax & Compliance'
    
    def ready(self):
        # Import signals to ensure they are registered
        import compliance.signals