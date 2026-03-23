"""Tests for the CSV parser component (importer.parser).

Covers: happy path, missing file, missing columns, empty file,
whitespace stripping, and partial-row skipping.
"""

import csv
from pathlib import Path

import pytest
from importer.exceptions import FileFormatError
from importer.models import User
from importer.parser import parse_csv

# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_parse_valid_csv_returns_correct_count(valid_csv: Path) -> None:
    """Three data rows should yield exactly three User objects."""
    users = list(parse_csv(valid_csv))
    assert len(users) == 3


def test_parse_valid_csv_yields_user_instances(valid_csv: Path) -> None:
    """Every yielded item must be a User dataclass instance."""
    users = list(parse_csv(valid_csv))
    assert all(isinstance(u, User) for u in users)


def test_parse_valid_csv_correct_fields(valid_csv: Path) -> None:
    """First row should map to the expected field values."""
    users = list(parse_csv(valid_csv))
    assert users[0].user_id == "U001"
    assert users[0].name == "Alice Johnson"
    assert users[0].email == "alice@example.com"


def test_parse_empty_csv_yields_nothing(tmp_path: Path) -> None:
    """A CSV with only a header row should yield zero users."""
    f = tmp_path / "empty.csv"
    f.write_text("user_id,name,email\n", encoding="utf-8")
    assert list(parse_csv(f)) == []


# ---------------------------------------------------------------------------
# Error-path tests
# ---------------------------------------------------------------------------


def test_parse_missing_file_raises_file_format_error(tmp_path: Path) -> None:
    """A non-existent path must raise FileFormatError with 'File not found'."""
    with pytest.raises(FileFormatError, match="File not found"):
        list(parse_csv(tmp_path / "nonexistent.csv"))


def test_parse_missing_required_column_raises(tmp_path: Path) -> None:
    """A CSV missing the 'email' column must raise FileFormatError."""
    bad = tmp_path / "no_email.csv"
    bad.write_text("user_id,name\nU001,Alice\n", encoding="utf-8")
    with pytest.raises(FileFormatError, match="CSV must contain columns"):
        list(parse_csv(bad))


def test_parse_completely_empty_file_raises(tmp_path: Path) -> None:
    """A zero-byte file has no fieldnames and must raise FileFormatError."""
    empty = tmp_path / "zero.csv"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(FileFormatError, match="CSV must contain columns"):
        list(parse_csv(empty))


# ---------------------------------------------------------------------------
# Whitespace-stripping tests (parametrize)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw_id, raw_name, raw_email, expected_id, expected_email",
    [
        ("  U001  ", "Alice", "  alice@example.com  ", "U001", "alice@example.com"),
        ("\tU002\t", "  Bob  ", "bob@example.com", "U002", "bob@example.com"),
        ("U003", "Carlos", " carlos@example.com", "U003", "carlos@example.com"),
    ],
)
def test_parse_strips_whitespace_from_fields(
    tmp_path: Path,
    raw_id: str,
    raw_name: str,
    raw_email: str,
    expected_id: str,
    expected_email: str,
) -> None:
    """Leading/trailing whitespace in any field must be stripped."""
    f = tmp_path / "ws.csv"
    with f.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["user_id", "name", "email"])
        writer.writeheader()
        writer.writerow({"user_id": raw_id, "name": raw_name, "email": raw_email})

    users = list(parse_csv(f))
    assert users[0].user_id == expected_id
    assert users[0].email == expected_email


# ---------------------------------------------------------------------------
# Extra-columns tolerance test
# ---------------------------------------------------------------------------


def test_parse_ignores_extra_columns(tmp_path: Path) -> None:
    """Extra columns beyond the required three should be silently ignored."""
    f = tmp_path / "extra.csv"
    with f.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["user_id", "name", "email", "phone", "country"]
        )
        writer.writeheader()
        writer.writerow(
            {
                "user_id": "U001",
                "name": "Alice",
                "email": "alice@example.com",
                "phone": "123",
                "country": "Ghana",
            }
        )
    users = list(parse_csv(f))
    assert len(users) == 1
    assert users[0].user_id == "U001"
