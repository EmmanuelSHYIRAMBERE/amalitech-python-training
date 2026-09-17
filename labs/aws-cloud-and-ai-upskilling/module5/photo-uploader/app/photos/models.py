"""Photo model -- matches the existing Postgres table created by the Node
app's ensureSchema(): id UUID PK, s3_key TEXT, description TEXT,
created_at TIMESTAMPTZ DEFAULT now()."""

from __future__ import annotations

import uuid

from django.db import models


class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    s3_key = models.TextField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "photos"  # exact existing table name -- no app-label prefix
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Photo({self.id}, {self.s3_key})"
