"""Module 6 schema migration.

Adds:
  - Tag model
  - Click model
  - URL.owner (ForeignKey → users.User, nullable for backward compat)
  - URL.custom_alias
  - URL.tags (M2M → Tag)
  - URL.click_count
  - URL.is_active
  - URL.expires_at
  - URL.title / description / favicon
  - Composite indexes on URL and Click
"""

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shortener", "0001_initial"),
        ("users", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── Tag ──────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="Tag",
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
                ("name", models.CharField(max_length=50, unique=True)),
            ],
            options={"ordering": ["name"]},
        ),
        # ── New URL fields ────────────────────────────────────────────────────
        migrations.AddField(
            model_name="url",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="urls",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="url",
            name="custom_alias",
            field=models.CharField(
                blank=True,
                help_text="Premium vanity alias (e.g. 'my-shop'). Must be unique.",
                max_length=50,
                null=True,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name="url",
            name="click_count",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Denormalised counter incremented on every redirect.",
            ),
        ),
        migrations.AddField(
            model_name="url",
            name="is_active",
            field=models.BooleanField(
                db_index=True,
                default=True,
                help_text="Inactive URLs return 404 on redirect.",
            ),
        ),
        migrations.AddField(
            model_name="url",
            name="expires_at",
            field=models.DateTimeField(
                blank=True,
                db_index=True,
                help_text="Optional expiry. Null means the link never expires.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="url",
            name="title",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="url",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="url",
            name="favicon",
            field=models.URLField(blank=True, max_length=512, null=True),
        ),
        # ── URL.tags M2M ──────────────────────────────────────────────────────
        migrations.AddField(
            model_name="url",
            name="tags",
            field=models.ManyToManyField(
                blank=True, related_name="urls", to="shortener.tag"
            ),
        ),
        # ── URL indexes ───────────────────────────────────────────────────────
        migrations.AddIndex(
            model_name="url",
            index=models.Index(fields=["created_at"], name="url_created_at_idx"),
        ),
        migrations.AddIndex(
            model_name="url",
            index=models.Index(
                fields=["is_active", "expires_at"], name="url_active_expires_idx"
            ),
        ),
        # ── Click ─────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="Click",
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
                ("clicked_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "ip_address",
                    models.GenericIPAddressField(protocol="both", unpack_ipv4=True),
                ),
                ("user_agent", models.TextField(blank=True, default="")),
                ("country", models.CharField(blank=True, max_length=100, null=True)),
                ("city", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "referrer",
                    models.URLField(
                        blank=True,
                        help_text="The page the visitor came from (HTTP Referer header).",
                        max_length=2048,
                        null=True,
                    ),
                ),
                (
                    "url",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="clicks",
                        to="shortener.url",
                    ),
                ),
            ],
            options={"ordering": ["-clicked_at"]},
        ),
        migrations.AddIndex(
            model_name="click",
            index=models.Index(
                fields=["url", "country"], name="click_url_country_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="click",
            index=models.Index(
                fields=["url", "clicked_at"], name="click_url_time_idx"
            ),
        ),
    ]
