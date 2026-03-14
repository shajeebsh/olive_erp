from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("dashboard.urls")),
    path("finance/", include("finance.urls")),
    path("inventory/", include("inventory.urls")),
    path("hr/", include("hr.urls")),
    path("crm/", include("crm.urls")),
    path("projects/", include("projects.urls")),
    path("purchasing/", include("purchasing.urls")),
    path("reporting/", include("reporting.urls")),
    path("compliance/", include("compliance.urls")),
    path("company/", include("company.urls")),
    path("core/", include("core.urls")),
    # For now, let Wagtail handle everything from the root
    path("cms/", include(wagtail_urls)),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
