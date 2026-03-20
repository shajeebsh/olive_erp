from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from company.models import CompanyProfile

User = get_user_model()

class SingleCountryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', email='test@example.com')
        
        # Create a company profile with Ireland as the country
        self.company = CompanyProfile.objects.create(
            name='Test Ireland Company',
            address='123 Test St',
            phone='1234567890',
            email='test@example.com',
            country_code='IE',
            fiscal_year_start_date='2025-01-01',
            financial_year_end='2025-12-31'
        )
        self.user.company = self.company
        self.user.save()
        
        # Login AFTER setting company
        self.client.login(username='testuser', password='password123')
    
    def test_navigation_menu_ie(self):
        """Test that navigation menu shows only Ireland-specific items when country is IE"""
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        
        # Should contain Ireland items
        self.assertIn('VAT3 Return', html)
        self.assertIn('CRO B1', html)
        
        # Should NOT contain other country items
        self.assertNotIn('GSTR-3B', html)
        self.assertNotIn('VAT Return', html) # UK version
        self.assertNotIn('VAT 201', html) # UAE version
        
        # Should also contain non-compliance submenus
        self.assertIn('Invoices', html)
        self.assertIn('Products', html)
        self.assertIn('Customers', html)
        self.assertIn('Employees', html)
        self.assertIn('Active Projects', html)
        self.assertIn('Suppliers', html)
    
    def test_navigation_menu_ae(self):
        """Test that navigation menu shows only UAE-specific items when country is AE"""
        self.company.country_code = 'AE'
        self.company.save()
        
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        
        # Should contain UAE items
        self.assertIn('VAT 201', html)
        self.assertIn('Excise Tax', html)
        
        # Should NOT contain Ireland items
        self.assertNotIn('VAT3 Return', html)
        self.assertNotIn('CRO B1', html)
    
    def test_dashboard_filters_by_country(self):
        """Test that compliance dashboard shows the correct country header"""
        response = self.client.get(reverse('compliance:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Compliance Dashboard')
        
        self.company.country_code = 'AE'
        self.company.save()
        response = self.client.get(reverse('compliance:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AE')

    def test_api_endpoints_filter_by_country(self):
        """Test that API endpoints return data filtered by company country"""
        # Ireland
        response = self.client.get(reverse('compliance:api_deadlines'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for event in data:
            self.assertEqual(event['country'], 'IE')
            
        # Switch to India
        self.company.country_code = 'IN'
        self.company.save()
        response = self.client.get(reverse('compliance:api_deadlines'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for event in data:
            self.assertEqual(event['country'], 'IN')

    def test_setup_wizard_new_user(self):
        """Test that a new user without a company can access and submit setup step 2"""
        # Create a new user without a company profile
        new_user = User.objects.create_user(username='new_setup_user', password='password123', email='new@example.com')
        self.client.login(username='new_setup_user', password='password123')
        
        # Access step 2 (assuming step 1 was skipped or completed without company creation yet)
        response = self.client.get(reverse('company:setup_features'))
        self.assertEqual(response.status_code, 200)
        
        # Submit step 2 form
        post_data = {
            'country': 'GB',
            'features': ['finance', 'inventory']
        }
        response = self.client.post(reverse('company:setup_features'), post_data)
        
        # Should redirect to step 3 on success, not throw 500 error
        self.assertRedirects(response, reverse('company:setup_step3'))
        
        # Check session data is stored correctly
        session = self.client.session
        self.assertEqual(session.get('setup_country'), 'GB')
