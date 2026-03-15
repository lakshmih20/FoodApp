# FSSAI OCR and risk assessment settings
FSSAI_OCR_CONFIDENCE_THRESHOLD = 0.6
FSSAI_NUMBER_LENGTH = 14
FSSAI_AUTO_APPROVE_LOW_RISK = False  # Set True to auto-verify low risk
"""
Django settings for homefood project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]
ALLOWED_HOSTS.append('testserver')
ALLOWED_HOSTS.append('192.168.1.3')  # Added for external access from phone
# Allow LAN access for mobile testing (phone on same Wi‑Fi)
# When you change WiFi, add your new PC IP here and to CSRF_TRUSTED_ORIGINS below.
if DEBUG:
    for extra in ('10.57.61.48', '172.25.64.1', '192.168.1.3', '192.168.1.4'):
        if extra not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(extra)

CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in os.getenv('CSRF_TRUSTED_ORIGINS', 'http://10.57.61.48:8000,http://192.168.1.3:8000,http://192.168.1.4:8000').split(',')
    if origin.strip()
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    # Custom apps
    'apps.accounts',
    'apps.cooks',
    'apps.buyers',
    'apps.admin_panel',
    'apps.payments',
    
    'apps.notifications',
    'apps.live_streaming',
        # Removed 'apps.ml_engine' to fix ModuleNotFoundError
        # 'apps.ml_engine',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'homefood.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'homefood.context_processors.google_maps_api_key',
            ],
        },
    },
]

WSGI_APPLICATION = 'homefood.wsgi.application'
ASGI_APPLICATION = 'homefood.asgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Database configuration - supports both SQLite and MySQL
USE_SQLITE = os.getenv('USE_SQLITE', 'False') == 'True'

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            # Increase timeout so SQLite waits for locks instead of failing immediately
            'OPTIONS': {
                'timeout': 20,
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'homefood_db'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Login URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:profile'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Razorpay Settings
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')



# MSG91 Settings
MSG91_AUTH_KEY = os.getenv('MSG91_AUTH_KEY', '')
MSG91_SENDER_ID = os.getenv('MSG91_SENDER_ID', '')

# Live Streaming (AWS IVS or Agora) - keep secrets in .env
LIVE_STREAM_PROVIDER = os.getenv('LIVE_STREAM_PROVIDER', 'aws_ivs')
AWS_IVS_PLAYBACK_BASE_URL = os.getenv('AWS_IVS_PLAYBACK_BASE_URL', '')
AWS_IVS_INGEST_BASE_URL = os.getenv('AWS_IVS_INGEST_BASE_URL', '')
AWS_REGION= os.getenv('AWS_REGION', 'ap-south-1')
AGORA_APP_ID = os.getenv('AGORA_APP_ID', '')
AGORA_APP_CERTIFICATE = os.getenv('AGORA_APP_CERTIFICATE', '')

# Django Channels (needed for live-stream WebSocket chat)
REDIS_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
# Use in-memory layer in development so chat works without Redis; use Redis in production.
if DEBUG:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [('127.0.0.1', 6379)],
            },
        },
    }

# Cache (used for chat rate limiting)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'live-streaming-cache',
    }
}

# Live chat security controls
LIVE_CHAT_MAX_MESSAGE_LENGTH = 500
LIVE_CHAT_MIN_SECONDS_BETWEEN_MESSAGES = 2

