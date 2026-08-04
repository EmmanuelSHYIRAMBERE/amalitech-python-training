"""ASGI entry point for the URL Shortener Microservice.

Enables async views (e.g. HealthCheckView) and allows the project to run
under uvicorn for higher concurrency than the WSGI/gunicorn setup.

Usage::

    uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --workers 2
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_asgi_application()
