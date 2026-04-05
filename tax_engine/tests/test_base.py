from django.test import TestCase
from tax_engine.registry import registry
from tax_engine.base.engines import BaseTaxEngine

class RegistryTests(TestCase):
    def test_registry_singleton(self):
        r1 = registry
        r2 = registry
        self.assertIs(r1, r2)

    def test_country_registration(self):
        # Test that our placeholder countries are registered
        countries = registry.get_all_countries()
        codes = [c['code'] for c in countries]

        self.assertIn('IE', codes)
        self.assertIn('GB', codes)
        self.assertIn('IN', codes)
        self.assertIn('AE', codes)

    def test_get_tax_engine(self):
        engine = registry.get_tax_engine('IE')
        self.assertIsNotNone(engine)
        self.assertEqual(engine.country_code, 'IE')

        engine = registry.get_tax_engine('XX')
        self.assertIsNone(engine)

class BaseEngineTests(TestCase):
    def test_base_engine_abstract(self):
        # Ensure BaseTaxEngine cannot be instantiated directly
        with self.assertRaises(TypeError):
            BaseTaxEngine()
