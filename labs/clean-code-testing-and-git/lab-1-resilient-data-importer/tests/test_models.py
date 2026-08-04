"""Tests for data models (importer.models) and exceptions (importer.exceptions).

Ensures the User dataclass serialises correctly and that the custom
exception hierarchy behaves as expected.
"""

import pytest
from importer.exceptions import (
    DuplicateUserError,
    FileFormatError,
    ImporterError,
    ValidationError,
)
from importer.models import User

# ---------------------------------------------------------------------------
# User dataclass tests
# ---------------------------------------------------------------------------


def test_user_fields_are_set_correctly() -> None:
    """Constructor arguments must be stored in the correct attributes."""
    user = User(user_id="U001", name="Alice", email="alice@example.com")
    assert user.user_id == "U001"
    assert user.name == "Alice"
    assert user.email == "alice@example.com"


def test_user_imported_at_is_auto_populated() -> None:
    """imported_at must be set automatically and be a non-empty string."""
    user = User(user_id="U001", name="Alice", email="alice@example.com")
    assert isinstance(user.imported_at, str)
    assert len(user.imported_at) > 0


def test_user_to_dict_contains_all_keys() -> None:
    """to_dict() must return a dict with all four expected keys."""
    user = User(user_id="U001", name="Alice", email="alice@example.com")
    d = user.to_dict()
    assert set(d.keys()) == {"user_id", "name", "email", "imported_at"}


def test_user_to_dict_values_match_fields() -> None:
    """to_dict() values must match the corresponding dataclass fields."""
    user = User(user_id="U001", name="Alice", email="alice@example.com")
    d = user.to_dict()
    assert d["user_id"] == "U001"
    assert d["name"] == "Alice"
    assert d["email"] == "alice@example.com"
    assert d["imported_at"] == user.imported_at


def test_user_custom_imported_at_is_preserved() -> None:
    """An explicitly provided imported_at value must not be overwritten."""
    user = User(
        user_id="U001",
        name="Alice",
        email="alice@example.com",
        imported_at="2024-01-01T00:00:00+00:00",
    )
    assert user.imported_at == "2024-01-01T00:00:00+00:00"


# ---------------------------------------------------------------------------
# Exception hierarchy tests
# ---------------------------------------------------------------------------


def test_file_format_error_is_importer_error() -> None:
    """FileFormatError must be a subclass of ImporterError."""
    assert issubclass(FileFormatError, ImporterError)


def test_duplicate_user_error_is_importer_error() -> None:
    """DuplicateUserError must be a subclass of ImporterError."""
    assert issubclass(DuplicateUserError, ImporterError)


def test_validation_error_is_importer_error() -> None:
    """ValidationError must be a subclass of ImporterError."""
    assert issubclass(ValidationError, ImporterError)


def test_duplicate_user_error_stores_user_id() -> None:
    """DuplicateUserError must expose the offending user_id as an attribute."""
    exc = DuplicateUserError("U042")
    assert exc.user_id == "U042"


def test_duplicate_user_error_message_contains_user_id() -> None:
    """DuplicateUserError message must mention the duplicate user_id."""
    exc = DuplicateUserError("U042")
    assert "U042" in str(exc)


def test_all_custom_exceptions_are_catchable_as_importer_error() -> None:
    """All custom exceptions must be catchable via the base ImporterError."""
    for exc_cls in (FileFormatError, DuplicateUserError, ValidationError):
        with pytest.raises(ImporterError):
            if exc_cls is DuplicateUserError:
                raise exc_cls("U001")
            else:
                raise exc_cls("test message")
