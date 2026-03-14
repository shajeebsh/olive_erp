from django.apps import AppConfig
import importlib
import pkgutil
import logging

logger = logging.getLogger(__name__)

class ComplianceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'compliance'

    def ready(self):
        """
        Auto-discover all country modules when Django starts.
        This allows adding new countries without modifying core code.
        """
        self.discover_countries()

    def discover_countries(self):
        """
        Scan the 'countries' directory and import all modules.
        Each country module should register itself with the registry.
        """
        try:
            # Import the countries package
            from . import countries
            
            # Iterate through all modules in countries package
            for _, module_name, _ in pkgutil.iter_modules(countries.__path__):
                if not module_name.startswith('_'):
                    try:
                        # Import the module (this will trigger registration)
                        importlib.import_module(f'compliance.countries.{module_name}')
                        logger.info(f"Loaded country module: {module_name}")
                    except Exception as e:
                        logger.error(f"Failed to load country module {module_name}: {e}")
        except ImportError:
            logger.warning("No countries module found - create compliance/countries/")
        except Exception as e:
            logger.error(f"Error discovering countries: {e}")