"""Tests for src.activity — log_activity and get_activity."""

from unittest.mock import MagicMock, patch


def test_log_activity_calls_insert_one(mock_collection: object) -> None:
    with patch("src.activity._activity", return_value=mock_collection):
        from src.activity import log_activity

        log_activity(1, "liked_post", {"post_id": 3})
    mock_collection.insert_one.assert_called_once()  # type: ignore[attr-defined]


def test_log_activity_stores_correct_fields(mock_collection: object) -> None:
    with patch("src.activity._activity", return_value=mock_collection):
        from src.activity import log_activity

        log_activity(2, "followed_user", {"user_id": 5})
    doc = mock_collection.insert_one.call_args[0][0]  # type: ignore[attr-defined]
    assert doc["actor_id"] == 2
    assert doc["action"] == "followed_user"
    assert doc["target"] == {"user_id": 5}
    assert "timestamp" in doc


def test_get_activity_returns_list(mock_collection: object) -> None:
    expected = [{"actor_id": 1, "action": "liked_post", "target": {"post_id": 3}}]
    cursor_mock = MagicMock()
    cursor_mock.sort.return_value = cursor_mock
    cursor_mock.limit.return_value = iter(expected)
    mock_collection.find.return_value = cursor_mock  # type: ignore[attr-defined]
    with patch("src.activity._activity", return_value=mock_collection):
        from src.activity import get_activity

        result = get_activity(1)
    assert result == expected


def test_get_activity_excludes_mongo_id(mock_collection: object) -> None:
    cursor_mock = MagicMock()
    cursor_mock.sort.return_value = cursor_mock
    cursor_mock.limit.return_value = iter([])
    mock_collection.find.return_value = cursor_mock  # type: ignore[attr-defined]
    with patch("src.activity._activity", return_value=mock_collection):
        from src.activity import get_activity

        get_activity(1)
    projection = mock_collection.find.call_args[0][1]  # type: ignore[attr-defined]
    assert projection == {"_id": 0}


def test_get_activity_sorts_by_timestamp_desc(mock_collection: object) -> None:
    cursor_mock = MagicMock()
    cursor_mock.sort.return_value = cursor_mock
    cursor_mock.limit.return_value = iter([])
    mock_collection.find.return_value = cursor_mock  # type: ignore[attr-defined]
    with patch("src.activity._activity", return_value=mock_collection):
        from src.activity import get_activity

        get_activity(1)
    cursor_mock.sort.assert_called_once_with("timestamp", -1)
