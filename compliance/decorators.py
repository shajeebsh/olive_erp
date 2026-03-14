"""
Decorators for easy country registration
"""
from .registry import registry

def register_tax_engine(country_code):
    """
    Decorator to register a tax engine.
    """
    def decorator(cls):
        registry.register(country_code, cls)
        return cls
    return decorator


def register_compliance_engine(country_code):
    """
    Decorator to register a compliance engine.
    """
    def decorator(cls):
        # Get existing tax engine or None
        tax_engine = registry._tax_engines.get(country_code)
        registry.register(country_code, tax_engine, cls)
        return cls
    return decorator
