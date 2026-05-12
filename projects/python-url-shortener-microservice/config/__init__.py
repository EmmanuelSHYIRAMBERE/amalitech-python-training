# This makes the Celery app available as config.celery_app so that
# Django's AppRegistry is fully loaded before Celery tasks are discovered.
# Without this, tasks that import Django models would fail at import time.
#
# The try/except guard allows mypy and pre-commit to import this module
# even when celery is not installed in their isolated environments.
try:
    from .celery import app as celery_app

    __all__ = ["celery_app"]
except ImportError:  # pragma: no cover
    pass
