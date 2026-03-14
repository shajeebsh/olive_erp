from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from company.models import CompanyProfile

User = get_user_model()

class SetupWizardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123', email='test@example.com')
        self.client.login(username='testuser', password='password123')

    def test_middleware_redirects_to_setup_when_no_company(self):
        """Authenticated users without a company should be redirected to setup."""
        response = self.client.get(reverse('dashboard:index'))
        self.assertRedirects(response, reverse('company:setup'))

    def test_setup_form_creation(self):
        """Step 1 should render the company profile form."""
        response = self.client.get(reverse('company:setup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'company/setup/step1_company.html')

    def test_no_redirect_when_company_exists(self):
        """Users should NOT be redirected away from setup if a company exists (Update mode)."""
        from django.utils import timezone
        CompanyProfile.objects.create(
            name="Test Corp", 
            fiscal_year_start_date=timezone.now().date()
        )
        response = self.client.get(reverse('company:setup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Corp")

    def test_feature_setup_post_redirects_to_complete(self):
        """Step 2 POST should redirect to completion page."""
        from django.utils import timezone
        CompanyProfile.objects.create(
            name="Test Corp", 
            fiscal_year_start_date=timezone.now().date()
        )
        response = self.client.post(reverse('company:setup_features'), {'load_sample_data': 'on'})
        self.assertRedirects(response, reverse('company:setup_complete'))
