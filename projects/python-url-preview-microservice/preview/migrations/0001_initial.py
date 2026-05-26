"""Initial migration for the preview app — no models needed (stateless service).

The preview service is intentionally stateless: it fetches metadata on demand
and returns it without persisting anything. Circuit-breaker state lives in Redis.

This empty migration satisfies Django's migration framework requirement
when INSTALLED_APPS includes 'preview'.
"""
from __future__ import annotations

from typing import ClassVar

from django.db import migrations


class Migration(migrations.Migration):

    initial = True
    dependencies: ClassVar[list[tuple[str, str]]] = []
    operations: ClassVar[list[migrations.operations.base.Operation]] = []
