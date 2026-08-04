"""Tests for the validation component (importer.validator).

Uses pytest.mark.parametrize extensively to cover valid inputs, each
distinct invalid field, and edge-case email formats.
"""

import pytest
from importer.exceptions import ValidationError
from importer.models import User
from importer.validator import validate_user

# ---------------------------------------------------------------------------
# Valid user tests (parametrize)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "user_id, name, email",
    [
        ("U001", "Alice Johnson", "alice@example.com"),
        ("U002", "Bob Smith", "bob.smith+tag@domain.co.uk"),
        ("U999", "Carlos", "carlos@subdomain.example.org"),
        ("X1", "D", "d@d.io"),  # minimal valid name (single char)
    ],
)
def test_valid_users_do_not_raise(user_id: str, name: str, email: str) -> None:
    """Well-formed User records must pass validation without raising."""
    validate_user(User(user_id=user_id, name=name, email=email))  # no exception


# ---------------------------------------------------------------------------
# Invalid user_id tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad_id", ["", "   ", "\t"])
def test_empty_user_id_raises_validation_error(bad_id: str) -> None:
    """Blank or whitespace-only user_id must raise ValidationError."""
    with pytest.raises(ValidationError, match="user_id is empty"):
        validate_user(User(user_id=bad_id, name="Alice", email="alice@example.com"))


# ---------------------------------------------------------------------------
# Invalid name tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad_name", ["", "   ", "\n"])
def test_empty_name_raises_validation_error(bad_name: str) -> None:
    """Blank or whitespace-only name must raise ValidationError."""
    with pytest.raises(ValidationError, match="name is empty"):
        validate_user(User(user_id="U001", name=bad_name, email="alice@example.com"))


# ---------------------------------------------------------------------------
# Invalid email tests (parametrize)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_email, description",
    [
        ("not-an-email", "no @ symbol"),
        ("missing@tld.", "TLD ends with dot"),
        ("@nodomain.com", "no local part"),
        ("spaces in@email.com", "space in local part"),
        ("double@@domain.com", "double @"),
        ("nodot@domain", "no TLD at all"),
        ("", "empty string"),
    ],
)
def test_invalid_email_raises_validation_error(
    bad_email: str, description: str
) -> None:
    """Invalid email formats must raise ValidationError with 'Invalid email'."""
    with pytest.raises(ValidationError, match="Invalid email"):
        validate_user(User(user_id="U001", name="Alice", email=bad_email))


# ---------------------------------------------------------------------------
# Error message content tests
# ---------------------------------------------------------------------------


def test_validation_error_message_contains_user_id() -> None:
    """The ValidationError message for a bad email must include the user_id."""
    with pytest.raises(ValidationError, match="U042"):
        validate_user(User(user_id="U042", name="Alice", email="bad"))


def test_validation_error_message_contains_email() -> None:
    """The ValidationError message must include the offending email value."""
    with pytest.raises(ValidationError, match="bad-email"):
        validate_user(User(user_id="U001", name="Alice", email="bad-email"))
