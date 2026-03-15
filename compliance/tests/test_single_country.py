from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from company.models import CompanyProfile, Currency

User = get_user_model()


class SingleCountryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123", email="test@example.com"
        )

        # Create currency first
        self.currency = Currency.objects.create(code="EUR", name="Euro", symbol="€")

        # Create company profile
        self.company = CompanyProfile.objects.create(
            name="Test Co",
            country_code="IE",
            address="123 Test St",
            phone="123456789",
            email="test@test.com",
            fiscal_year_start_date=date(2025, 1, 1),
            default_currency=self.currency,
        )
        # Link user to company if needed (assuming there's a relation or it's global)
        # In this project, CompanyProfile.objects.first() is often used.

        self.client.login(username="testuser", password="password123")

    def test_menu_shows_only_ie_items(self):
        response = self.client.get(reverse("dashboard:index"))
        html = response.content.decode()

        # Should contain Ireland-specific items
        self.assertIn("VAT3 Return", html)
        self.assertIn("CRO B1", html)

        # Should NOT contain other countries' items
        self.assertNotIn("GSTR-3B", html)
        self.assertNotIn("VAT 201", html)
        self.assertNotIn("CT600", html)

    def test_dashboard_filters_by_country(self):
        response = self.client.get(reverse("compliance:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["company"].country_code, "IE")
        self.assertContains(response, "🇮🇪 Ireland Compliance Dashboard")

    def test_api_filters_by_country(self):
        response = self.client.get(reverse("api_compliance:deadlines"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for event in data:
            self.assertEqual(event["country"], "IE")

    def test_switch_country_and_check_menu(self):
        # Change company country to India
        self.company.country_code = "IN"
        self.company.save()

        response = self.client.get(reverse("dashboard:index"))
        html = response.content.decode()

        # Should contain India-specific items
        self.assertIn("GSTR-3B", html)
        self.assertIn("GSTR-1", html)

        # Should NOT contain Ireland items
        self.assertNotIn("VAT3 Return", html)
        self.assertNotIn("CRO B1", html)
