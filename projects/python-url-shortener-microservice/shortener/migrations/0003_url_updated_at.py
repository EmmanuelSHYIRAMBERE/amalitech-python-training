# Generated manually — adds updated_at column that was missing from 0001_initial.
# The column was added directly via ALTER TABLE on the running container;
# this migration records that change so the migration history stays consistent.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shortener", "0002_alter_url_original_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="url",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
