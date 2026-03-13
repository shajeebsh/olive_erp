from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from company.models import CompanyProfile

class CompanySetupMiddleware:
    """
    Middleware that checks if a CompanyProfile exists.
    If not, it redirects all authenticated users (except admin/static) to the setup wizard.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        excluded_prefixes = [
            '/static/', '/media/', '/admin/', '/setup/', '/company/setup/',
            '/accounts/login/', '/accounts/logout/',
        ]
        if not any(path.startswith(prefix) for prefix in excluded_prefixes):
            if request.user.is_authenticated:
                if not CompanyProfile.objects.exists():
                    return redirect(reverse('company:setup'))
        
        response = self.get_response(request)
        return response
