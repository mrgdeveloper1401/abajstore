import os
from pathlib import Path
from decouple import config
from datetime import timedelta


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


DEBUG = config('DEBUG', cast=bool, default=False)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_filters',
    'corsheaders',
    'django_extensions',
    'rest_framework',
    'rest_framework_simplejwt',

    'accounts',
    'products',
    'carts',
    'orders',
    'site_settings',
    "catalog_app",
    "core_app"
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# 🔹 تنظیم اعتبار توکن روی 30 روز
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),  # توکن 30 روز معتبر است
    'REFRESH_TOKEN_LIFETIME': timedelta(days=60),  # توکن Refresh برای 60 روز معتبر است
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'abajstore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'products.custom_context_processors.category',
                'carts.custom_context_processors.cart',
                'site_settings.custom_context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'abajstore.wsgi.application'


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
LANGUAGE_CODE = 'fa-ir'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# تنظیمات مدیا
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "accounts.User"

LOGIN_URL = 'auth:login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', cast=str)
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', cast=str)
RECEIVER_EMAIL_FOR_INVOICE = config('RECEIVER_EMAIL_FOR_INVOICE', cast=str)


MELLAT_TERMINAL_CODE = config('MELLAT_TERMINAL_CODE', cast=str),
MELLAT_USERNAME = config('MELLAT_USERNAME', cast=str),
MELLAT_PASSWORD = config('MELLAT_PASSWORD', cast=str),
PAYMENT_GATEWAY_LOGIN = config('PARSIAN_PAYMENT_GATEWAY_LOGIN', cast=str)
SMS_API_KEY = config('SMS_API_KEY', cast=str)
SMS_AUTH_BASE64 = config('SMS_AUTH_BASE64', cast=str)
SMS_NUMBER = config('SMS_NUMBER', cast=str)
SEPANDYAR_IP = config('SEPANDYAR_IP', cast=str)
SEPANDYAR_USER = config('SEPANDYAR_USER', cast=str)
SEPANDYAR_PASS = config('SEPANDYAR_PASS', cast=str)


SESSION_ENGINE = 'django.contrib.sessions.backends.db'

LOG_DIR = BASE_DIR / "log_project"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "log.log"
