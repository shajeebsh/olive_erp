default_app_config = 'tax_engine.apps.TaxEngineConfig'

# Export main classes
from .registry import registry

__all__ = [
    'registry',
]
