"""Data migration — seed default Tag records.

Creates the initial set of tags that every deployment starts with.
Uses get_or_create so re-running is idempotent (safe in CI and staging).
"""

from django.db import migrations

DEFAULT_TAGS = [
    "Marketing",
    "Social",
    "News",
    "Technology",
    "Education",
    "Entertainment",
    "Finance",
    "Health",
    "Travel",
    "Other",
]


def seed_tags(apps, schema_editor):  # type: ignore[no-untyped-def]
    """Forward: create default tags."""
    Tag = apps.get_model("shortener", "Tag")
    for name in DEFAULT_TAGS:
        Tag.objects.get_or_create(name=name)


def unseed_tags(apps, schema_editor):  # type: ignore[no-untyped-def]
    """Reverse: remove only the seeded tags (leaves user-created ones intact)."""
    Tag = apps.get_model("shortener", "Tag")
    Tag.objects.filter(name__in=DEFAULT_TAGS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("shortener", "0002_mod6_schema"),
    ]

    operations = [
        migrations.RunPython(seed_tags, reverse_code=unseed_tags),
    ]
