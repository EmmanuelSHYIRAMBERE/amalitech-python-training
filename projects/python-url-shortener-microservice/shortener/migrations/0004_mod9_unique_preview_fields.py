"""Module 9 schema migration.

Adds unique constraints to URL.title, URL.description, and URL.favicon
as required by the project spec (CharField/TextField Nullable, Unique).
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shortener", "0003_seed_default_tags"),
    ]

    operations = [
        migrations.AlterField(
            model_name="url",
            name="title",
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="url",
            name="description",
            field=models.TextField(
                blank=True,
                null=True,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="url",
            name="favicon",
            field=models.URLField(
                blank=True,
                max_length=512,
                null=True,
                unique=True,
            ),
        ),
    ]
