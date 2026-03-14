default_app_config = 'compliance.apps.ComplianceConfig'

# Export main classes
from .registry import registry

__all__ = [
    'registry',
]
