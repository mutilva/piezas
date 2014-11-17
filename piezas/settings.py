#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Django settings for piezas project.
from django.utils.translation import ugettext_lazy as _
from oscar import get_core_apps
from oscar import OSCAR_MAIN_TEMPLATE_DIR
import os


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('POD Recambios', 'info@podrecambios.es'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'pod',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'pod',
        'PASSWORD': 'pod2014',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es-es'

SITE_ID = 2

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
PROJECT_DIR = os.path.dirname(__file__)
location = lambda x: os.path.join(
    os.path.dirname(os.path.realpath(__file__)), x)
MEDIA_ROOT = location("media")
MEDIA_URL = '/media/'
AJAXIMAGE_DIR = "searchpictures"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    location('static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '-@s3d!hdn1h=dvlea#s6z_m4-p0v1gz8m@r^ssjs8)l4f#h!!a'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
    'django.middleware.transaction.TransactionMiddleware',  # recommended for oscar
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'piezas.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'piezas.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    location('templates'),
    OSCAR_MAIN_TEMPLATE_DIR,
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'south',
    'compressor',
    'smart_selects',
    'ajaximage',
    'django_iban',
    'piezas.apps.customuser',
    'piezas.apps.dashboard.podcatalogue', 'piezas.apps.dashboard.podorders',
    'piezas.apps.dashboard.podusers', 'piezas.apps.dashboard'
]
INSTALLED_APPS = INSTALLED_APPS + get_core_apps([
    'piezas.apps.customer', 
    'piezas.apps.catalogue',
    'piezas.apps.order',
    'piezas.apps.search',
    'piezas.apps.address'
])

SITE_ID = 2

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'oscar.apps.search.context_processors.search_form',
    'oscar.apps.promotions.context_processors.promotions',
    'oscar.apps.checkout.context_processors.checkout',
    'oscar.apps.customer.notifications.context_processors.notifications',
    'oscar.core.context_processors.metadata',
)

AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.Emailbackend',
    'django.contrib.auth.backends.ModelBackend',
)

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

from oscar.defaults import *
OSCAR_SHOP_NAME = "POD recambios"
OSCAR_SHOP_TAGLINE = "Ahorra tiempo y dinero en la búsqueda de tu pieza recuperada"
OSCAR_DEFAULT_CURRENCY = 'EUR'
OSCAR_CURRENCY_LOCALE = 'es_ES'
OSCAR_ALLOW_ANON_REVIEWS = False
OSCAR_FROM_EMAIL = 'avisos@podrecambios.es'
LOGIN_REDIRECT_URL = '/'
LANGUAGES = ()

# Menu structure of the dashboard navigation
OSCAR_DASHBOARD_NAVIGATION = [
    {
        'label': _('Dashboard'),
        'icon': 'icon-th-list',
        'url_name': 'dashboard:index',
    },
    {
        'label': _('Catalogue'),
        'icon': 'icon-sitemap',
        'children': [
            {
                'label': _('Pieces'),
                'url_name': 'dashboard:catalogue-product-list',
            },
            {
                'label': _('Categories'),
                'url_name': 'dashboard:catalogue-category-list',
            },
            {
                'label': _('Brands'),
                'url_name': 'dashboard:catalogue-brand-list',
            },
            {
                'label': _('Models'),
                'url_name': 'dashboard:catalogue-model-list',
            },
            {
                'label': _('Versions'),
                'url_name': 'dashboard:catalogue-version-list',
            },
            {
                'label': _('Engine'),
                'url_name': 'dashboard:catalogue-engine-list',
            },
            {
                'label': _('Bodywork'),
                'url_name': 'dashboard:catalogue-bodywork-list',
            },
            {
                'label': _('Promotional code'),
                'url_name': 'dashboard:catalogue-promotionalcode-list',
            },
        ]
    },
    {
        'label': _('Fulfilment'),
        'icon': 'icon-shopping-cart',
        'children': [
            {
                'label': _('Order management'),
                'url_name': 'dashboard:order-list',
            },
            {
                'label': _('Search requests'),
                'url_name': 'dashboard:order-searchrequest-list',
            },
            {
                'label': _('Quotes'),
                'url_name': 'dashboard:quote-list',
            },
            {
                'label': _('Statistics'),
                'url_name': 'dashboard:order-stats',
            },
            {
                'label': _('Partners'),
                'url_name': 'dashboard:partner-list',
            },
        ]
    },
    {
        'label': _('Customers'),
        'icon': 'icon-group',
        'children': [
            {
                'label': _('Customer management'),
                'url_name': 'dashboard:users-index',
            }
        ]
    },
    {
        'label': _('Content'),
        'icon': 'icon-folder-close',
        'children': [
            {
                'label': _('Content blocks'),
                'url_name': 'dashboard:promotion-list',
            },
            {
                'label': _('Content blocks by page'),
                'url_name': 'dashboard:promotion-list-by-page',
            },
            {
                'label': _('Pages'),
                'url_name': 'dashboard:page-list',
            },
            {
                'label': _('Email templates'),
                'url_name': 'dashboard:comms-list',
            },
            {
                'label': _('Reviews'),
                'url_name': 'dashboard:reviews-list',
            },
        ] 
    },
    {
        'label': _('Reports'),
        'icon': 'icon-bar-chart',
        'url_name': 'dashboard:reports-index',
    },
]


LOCALE_PATHS = (location('../locale'),)
APPEND_SLASH = True
OSCAR_HOMEPAGE = '/'

EXCLUDE_TAXES = True
TPC_TAX = 21
AUTH_USER_MODEL = 'customuser.PiezasUser'
AUTH_USER_TABLE = 'piezasuser'
AJAXIMAGE_AUTH_TEST = (lambda u: True)
PHONENUMBER_DEFAULT_FORMAT = 'NATIONAL'

SEARCH_INTERVAL_MIN = 90

ORDER_STATUSES = ['pending_payment', 'paid', 'sent', 'canceled']
ORDER_STATUSES_DESC = [_('pending_payment'), _('paid'), _('sent'), _('canceled')]
