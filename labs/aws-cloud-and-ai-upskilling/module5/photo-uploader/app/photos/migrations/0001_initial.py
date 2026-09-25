import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies: list = []

    operations = [
        migrations.CreateModel(
            name="Photo",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("s3_key", models.TextField()),
                ("description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": "photos", "ordering": ["-created_at"]},
        ),
    ]
