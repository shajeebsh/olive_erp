"""
Country Registry - Central registry for all country implementations.
Follows the Registry pattern for pluggable architecture.
"""

class CountryRegistry:
    """
    Singleton registry for all country tax and compliance engines.
    """

    _instance = None
    _tax_engines = {}
    _compliance_engines = {}
    _country_configs = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, country_code, tax_engine_class, compliance_engine_class=None):
        """
        Register a country's tax and compliance engines.
        """
        cls._tax_engines[country_code] = tax_engine_class
        
        if compliance_engine_class:
            cls._compliance_engines[country_code] = compliance_engine_class

        # Store config from the engine
        engine = tax_engine_class()
        cls._country_configs[country_code] = {
            'name': engine.country_name,
            'currency': engine.currency_code,
            'tax_name': engine.tax_name,
        }
        return True

    @classmethod
    def get_tax_engine(cls, country_code):
        """Get tax engine instance for country"""
        engine_class = cls._tax_engines.get(country_code)
        if engine_class:
            return engine_class()
        return None

    @classmethod
    def get_compliance_engine(cls, country_code):
        """Get compliance engine instance for country"""
        engine_class = cls._compliance_engines.get(country_code)
        if engine_class:
            return engine_class()
        return None

    @classmethod
    def get_all_countries(cls):
        """Return list of all registered countries"""
        return [
            {'code': code, 'name': config['name'], 'currency': config['currency']}
            for code, config in cls._country_configs.items()
        ]

    @classmethod
    def get_active_countries(cls):
        return cls.get_all_countries()

    @classmethod
    def validate_tax_number(cls, country_code, tax_number):
        engine = cls.get_tax_engine(country_code)
        if engine:
            return engine.validate_tax_number(tax_number)
        return False, f"No engine found for country {country_code}"

# Create singleton instance
registry = CountryRegistry()
