"""Tests for the fetch_url_preview Celery task — Module 9.

Covers:
  - Task creates/updates title, description, favicon on the URL model
  - Task handles URL.DoesNotExist gracefully
  - Task handles preview service failure gracefully (no_metadata status)
  - Task queuing is triggered from URLCreateSerializer.create()
"""

from unittest.mock import patch

import pytest

from shortener.models import URL
from shortener.tasks import fetch_url_preview
from url_preview.service import PreviewResult
from users.models import User


# ---------------------------------------------------------------------------
# fetch_url_preview task — direct execution
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_fetch_url_preview_updates_url_fields(user: User) -> None:
    """Task writes title, description, favicon to the URL model."""
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="prev01",
        owner=user,
    )
    preview = PreviewResult(
        url="https://example.com",
        title="Example Domain",
        description="An example.",
        favicon="https://example.com/fav.ico",
    )

    with patch("shortener.tasks.get_url_preview", return_value=preview):
        result = fetch_url_preview(
            url_id=url.pk,
            original_url="https://example.com",
        )

    assert result["status"] == "success"
    url.refresh_from_db()
    assert url.title == "Example Domain"
    assert url.description == "An example."
    assert url.favicon == "https://example.com/fav.ico"


@pytest.mark.django_db
def test_fetch_url_preview_partial_update(user: User) -> None:
    """Task only updates fields that were successfully fetched."""
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="prev02",
        owner=user,
    )
    preview = PreviewResult(
        url="https://example.com",
        title="Only Title",
        # description and favicon are None
    )

    with patch("shortener.tasks.get_url_preview", return_value=preview):
        fetch_url_preview(url_id=url.pk, original_url="https://example.com")

    url.refresh_from_db()
    assert url.title == "Only Title"
    assert url.description is None
    assert url.favicon is None


@pytest.mark.django_db
def test_fetch_url_preview_returns_no_metadata_when_fetch_fails(user: User) -> None:
    """Task returns no_metadata status when preview service returns nothing."""
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="prev03",
        owner=user,
    )
    preview = PreviewResult(
        url="https://example.com",
        error="Circuit breaker open",
    )

    with patch("shortener.tasks.get_url_preview", return_value=preview):
        result = fetch_url_preview(url_id=url.pk, original_url="https://example.com")

    assert result["status"] == "no_metadata"
    assert result["error"] == "Circuit breaker open"
    url.refresh_from_db()
    assert url.title is None


@pytest.mark.django_db
def test_fetch_url_preview_handles_deleted_url() -> None:
    """Task returns url_deleted status when URL no longer exists."""
    result = fetch_url_preview(url_id=99999, original_url="https://example.com")
    assert result["status"] == "url_deleted"


# ---------------------------------------------------------------------------
# Integration: URLCreateSerializer queues the preview task
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_url_create_queues_preview_task(auth_client, sample_url_data) -> None:  # type: ignore[no-untyped-def]
    """Creating a short URL must queue fetch_url_preview.delay()."""
    with patch("shortener.serializers.fetch_url_preview") as mock_task:
        mock_task.delay = mock_task  # make .delay() callable
        with patch("shortener.serializers.fetch_url_preview.delay") as mock_delay:
            auth_client.post("/api/v1/urls/", sample_url_data, format="json")
    # The task must have been queued exactly once.
    mock_delay.assert_called_once()


@pytest.mark.django_db
def test_url_create_still_returns_201_when_preview_task_fails(
    auth_client, sample_url_data  # type: ignore[no-untyped-def]
) -> None:
    """A task-queuing failure must never break the create response."""
    with patch(
        "shortener.serializers.fetch_url_preview.delay",
        side_effect=Exception("broker down"),
    ):
        response = auth_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert response.status_code == 201
