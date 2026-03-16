from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Railway injects RAILWAY_PUBLIC_DOMAIN automatically
_railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
if _railway_domain and _railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_railway_domain)

# Allow all onrender.com subdomains
ALLOWED_HOSTS += ['.onrender.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'apps.core',
    'apps.waitlist',
    'apps.api',
    'apps.tools',
    'apps.content',
]

# Analytics
GA4_MEASUREMENT_ID = os.environ.get('GA4_MEASUREMENT_ID', '')
GSC_VERIFICATION = os.environ.get('GSC_VERIFICATION', '')
CLARITY_ID = os.environ.get('CLARITY_ID', '')
SENTRY_DSN = os.environ.get('SENTRY_DSN', '')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'reorderly.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'apps/core/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.analytics',
            ],
        },
    },
]

WSGI_APPLICATION = 'reorderly.wsgi.application'

# Database — uses DATABASE_URL in production, SQLite locally
_database_url = os.environ.get('DATABASE_URL', '')
if _database_url:
    DATABASES = {
        'default': dj_database_url.parse(_database_url, conn_max_age=600, ssl_require=not DEBUG)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'

STATICFILES_DIRS = []

# Add React build output if it exists
_frontend_dist = BASE_DIR / 'frontend' / 'dist'
if _frontend_dist.exists():
    STATICFILES_DIRS.append(_frontend_dist)

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS
_cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:5173')
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins.split(',') if o.strip()]

# CSRF trusted origins for production
_csrf_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if _csrf_origins:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_origins.split(',') if o.strip()]
elif _railway_domain:
    CSRF_TRUSTED_ORIGINS = [f'https://{_railway_domain}']
else:
    CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']

# Production security settings
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# DRF
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}
