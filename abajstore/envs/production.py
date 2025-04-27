from abajstore.settings import *

# import dj_database_url

SECRET_KEY = config("PROD_SECRET_KEY", cast=str)

ALLOWED_HOSTS = ['abajstore.ir']

MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware',)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # 'CONN_HEALTH_CHECKS': True,
        'NAME': config('DATABASE_NAME', cast=str),
        'USER': config('DATABASE_USER', cast=str),
        'PASSWORD': config('DATABASE_PASSWORD', cast=str),
        'PORT': config('PORT', cast=int),
        # 'CONN_MAX_AGE': 500,
        # 'OPTIONS': {
        #     'autocommit': True,
        #     'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        # }
    }
}

CORS_ALLOWED_ORIGINS = [
    "https://abajstore.ir",
    "http://abajstore.ir",
    "https://www.abajstore.ir",
    "http://www.abajstore.ir",
    "https://pec.shaparak.ir",
    "https://www.pec.shaparak.ir"
]

# CORS_ALLOW_CREDENTIALS = True

CSRF_COOKIE_DOMAIN = 'abajstore.ir'

CSRF_TRUSTED_ORIGINS = [
    'https://pec.shaparak.ir',
    'https://www.pec.shaparak.ir'
]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin"
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_DOMAIN = 'abajstore.ir'

SIMPLE_JWT['SIGNING_KEY'] = SECRET_KEY

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / LOG_FILE,
            "maxBytes": 1024 * 1024,
            "backupCount": 5,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
        }
    }
}