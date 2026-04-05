import os
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", cast=lambda v: [s.strip() for s in v.split(",")]
)

INSTALLED_APPS = [
    "core",
    "company",
    "finance",
    "inventory",
    "crm",
    "purchasing",
    "hr",
    "projects",
    "compliance",
    "reporting",
    "apps.accounting.assets",
    "apps.accounting.reconciliation",
    "apps.accounting.related_party",
    "apps.accounting.statutory",
    "apps.accounting.compliance",
    "apps.accounting.reporting",
    "dashboard",
    "home",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "rest_framework",
    "django_htmx",
    "django_celery_beat",
]

# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Beat schedule – runs daily at midnight
from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'generate-recurring-invoices-daily': {
        'task': 'finance.generate_recurring_invoices',
        'schedule': crontab(hour=0, minute=0),  # midnight daily
    },
    'send-compliance-reminders-daily': {
        'task': 'core.tasks.send_deadline_reminders',
        'schedule': crontab(hour=8, minute=0),  # 8 AM daily
    },
    'notify-vat-threshold-daily': {
        'task': 'core.tasks.notify_vat_threshold',
        'schedule': crontab(hour=9, minute=0),  # 9 AM daily
    },
}
# Country framework settings
COUNTRY_CONFIG = {
    'DEFAULT_COUNTRY': 'IE',
    'AUTO_DISCOVER_COUNTRIES': True,
    'COUNTRY_MODULES_PATH': 'compliance.countries',
}

# Tax calculation settings
TAX_SETTINGS = {
    'DECIMAL_PLACES': 2,
    'ROUNDING_METHOD': 'round_half_up',  # or 'round_up', 'round_down'
    'INCLUDE_TAX_IN_PRICE': False,  # True for countries where tax is included
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "core.middleware.CompanySetupMiddleware",
    "core.middleware.AuditMiddleware",
    "core.middleware.PermissionMiddleware",
]

ROOT_URLCONF = "wagtailerp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.navigation_menu",
            ],
        },
    },
]

WSGI_APPLICATION = "wagtailerp.wsgi.application"

import dj_database_url

# Default to SQLite for easier local development
DATABASE_URL = config("DATABASE_URL", default="sqlite:///db.sqlite3")
DATABASES = {
    "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, conn_health_checks=True)
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "core.User"

AUTHENTICATION_BACKENDS = [
    'core.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'login'

WAGTAIL_SITE_NAME = "Olive_ERP"
WAGTAILADMIN_BASE_URL = "http://localhost:8000"
