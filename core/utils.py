from typing import Optional
from company.models import CompanyProfile
from django.http import HttpRequest


def get_user_company(request: HttpRequest) -> Optional[CompanyProfile]:
    """
    Get the company associated with the current user.
    
    If the user has a company foreign key set, returns that company.
    Otherwise falls back to the first CompanyProfile in the system.
    Returns None if no company is found.
    """
    if hasattr(request.user, "company") and request.user.company:
        return request.user.company
    
    return CompanyProfile.objects.first()