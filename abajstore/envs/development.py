from abajstore.settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', cast=str)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

SIMPLE_JWT['SIGNING_KEY'] = SECRET_KEY

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / LOG_FILE,
            "maxBytes": 1024 * 1024,
            "backupCount": 5,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "INFO",
        }
    }
}
