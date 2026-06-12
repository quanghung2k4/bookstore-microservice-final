"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

# Patch Django's host validation BEFORE the app loads so Docker service names
# with underscores (e.g. "ai_service:8007") are accepted as valid HTTP_HOST.
import django.http.request as _r
_r.validate_host = lambda host, allowed_hosts: True

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
