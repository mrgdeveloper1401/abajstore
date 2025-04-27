"""
ASGI config for abajstore project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from decouple import config
from django.core.asgi import get_asgi_application

debug_mode = config('DEBUG', default=False, cast=bool)

if debug_mode:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abajstore.envs.development')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abajstore.envs.production')

application = get_asgi_application()
