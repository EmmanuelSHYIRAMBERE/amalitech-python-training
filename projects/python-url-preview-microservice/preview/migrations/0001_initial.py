"""Initial migration for the preview app — no models needed (stateless service).

The preview service is intentionally stateless: it fetches metadata on demand
and returns it without persisting anything. Circuit-breaker state lives in Redis.

This empty migration satisfies Django's migration framework requirement
when INSTALLED_APPS includes 'preview'.
"""
from django.db import migrations


class Migration(migrations.Migration):

    initial = True
    dependencies: list = []
    operations: list = []
