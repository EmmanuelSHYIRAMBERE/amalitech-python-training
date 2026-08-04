"""API v1 URL aggregator — all /api/v1/ routes live here."""

from django.urls import include, path

urlpatterns = [
    path("", include("preview.urls")),
    path("keys/", include("api_keys.urls")),
]
