"""Initial migration — creates the APIKey table."""

from __future__ import annotations

from typing import ClassVar

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies: ClassVar[list[tuple[str, str]]] = []

    operations = [
        migrations.CreateModel(
            name="APIKey",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "name",
                    models.CharField(
                        max_length=100, help_text="Friendly name for this key."
                    ),
                ),
                (
                    "token_hash",
                    models.CharField(db_index=True, max_length=64, unique=True),
                ),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("request_count", models.PositiveIntegerField(default=0)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="apikey",
            index=models.Index(
                fields=["is_active", "token_hash"],
                name="apikey_active_hash_idx",
            ),
        ),
    ]
