from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from company.models import CompanyProfile
import logging

logger = logging.getLogger(__name__)

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


class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            from .models import AuditLog
            # Simple audit log for write operations
            try:
                AuditLog.objects.create(
                    user=request.user,
                    action=request.method,
                    model_name="Request",
                    object_id="N/A",
                    object_repr=request.path_info,
                    ip_address=self.get_client_ip(request)
                )
            except Exception as e:
                logger.error(f"AuditMiddleware failed to create log: {e}")
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Attach permissions to request for easy access in templates/views
            company = getattr(request.user, 'company', None)
            if company:
                try:
                    request.company_permissions = request.user.get_company_permissions(company)
                except Exception as e:
                    logger.error(f"PermissionMiddleware failed to get permissions: {e}")
                    request.company_permissions = set()
            else:
                request.company_permissions = set()
        
        response = self.get_response(request)
        return response


# Module URL mappings
MODULE_URL_PATHS = {
    'finance': '/finance/',
    'inventory': '/inventory/',
    'crm': '/crm/',
    'hr': '/hr/',
    'projects': '/projects/',
    'reporting': '/reporting/',
    'compliance': '/compliance/',
}


class ModuleAccessMiddleware:
    """
    Middleware to enforce module-level access control based on company configuration.
    Blocks access to disabled module URLs.
    """
    EXEMPT_URLS = ['/admin/', '/django-admin/', '/accounts/', '/static/', '/media/']
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        
        # Skip exempt URLs
        if any(path.startswith(url) for url in self.EXEMPT_URLS):
            return self.get_response(request)
        
        # Determine module for this URL
        module_slug = None
        for mod, url_prefix in MODULE_URL_PATHS.items():
            if path.startswith(url_prefix):
                module_slug = mod
                break
        
        if not module_slug:
            return self.get_response(request)
        
        # Check company module access
        try:
            company = getattr(request.user, 'company', None)
            if company and not company.is_module_enabled(module_slug):
                from django.contrib import messages
                from django.http import HttpResponseForbidden
                messages.error(
                    request,
                    f"The {module_slug.title()} module is not enabled for your company."
                )
                return redirect('/')
        except Exception:
            pass  # Allow if no company found
        
        return self.get_response(request)
