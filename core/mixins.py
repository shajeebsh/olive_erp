from django.core.exceptions import PermissionDenied
from core.utils import get_user_company


class CompanyScopedMixin:
    """
    Mixin that ensures views are scoped to the user's company.
    Adds company to context and filters querysets by company.
    """
    
    def get_company(self):
        """Get the current user's company."""
        return get_user_company(self.request)
    
    def get_queryset(self):
        """Filter queryset by company if applicable."""
        qs = super().get_queryset()
        company = self.get_company()
        if company is None:
            return qs.none()
        
        # Check if model has company field
        if hasattr(qs.model, 'company'):
            return qs.filter(company=company)
        return qs
    
    def get_context_data(self, **kwargs):
        """Add company to context."""
        context = super().get_context_data(**kwargs)
        context['company'] = self.get_company()
        return context


class CompanyRequiredMixin(CompanyScopedMixin):
    """
    Mixin that requires a user to have an associated company.
    Raises PermissionDenied if no company is found.
    """
    
    def dispatch(self, request, *args, **kwargs):
        company = self.get_company()
        if company is None:
            raise PermissionDenied("No company associated with this user")
        return super().dispatch(request, *args, **kwargs)