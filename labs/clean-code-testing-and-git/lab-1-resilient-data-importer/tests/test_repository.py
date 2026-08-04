"""Tests for the storage repository component (importer.repository).

Covers: save, duplicate detection, count, exists, and the _open_db
context manager's read/write behaviour.
"""

import json
from pathlib import Path

import pytest
from importer.exceptions import DuplicateUserError
from importer.models import User
from importer.repository import UserRepository, _open_db

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _make_user(uid: str = "U001") -> User:
    return User(user_id=uid, name=f"User {uid}", email=f"{uid.lower()}@example.com")


# ---------------------------------------------------------------------------
# _open_db context manager tests
# ---------------------------------------------------------------------------


def test_open_db_creates_file_on_exit(tmp_path: Path) -> None:
    """_open_db must write the JSON file even if it did not exist before."""
    db = tmp_path / "new.json"
    with _open_db(db) as data:
        data["U001"] = {"name": "Alice"}
    assert db.exists()
    assert json.loads(db.read_text())["U001"]["name"] == "Alice"


def test_open_db_loads_existing_data(tmp_path: Path) -> None:
    """_open_db must load pre-existing records from disk."""
    db = tmp_path / "existing.json"
    db.write_text(json.dumps({"U001": {"name": "Alice"}}), encoding="utf-8")
    with _open_db(db) as data:
        assert "U001" in data


def test_open_db_writes_back_on_exception(tmp_path: Path) -> None:
    """_open_db must persist changes even when an exception is raised inside."""
    db = tmp_path / "exc.json"
    try:
        with _open_db(db) as data:
            data["U001"] = {"name": "Alice"}
            raise RuntimeError("simulated error")
    except RuntimeError:
        pass
    # Data written before the exception must still be on disk.
    assert "U001" in json.loads(db.read_text())


# ---------------------------------------------------------------------------
# UserRepository.save tests
# ---------------------------------------------------------------------------


def test_save_writes_user_to_database(db_path: Path) -> None:
    """Saving a user must persist it to the JSON file."""
    repo = UserRepository(db_path)
    repo.save(_make_user("U001"))
    data = json.loads(db_path.read_text())
    assert "U001" in data
    assert data["U001"]["name"] == "User U001"


def test_save_multiple_users(db_path: Path) -> None:
    """Multiple saves must accumulate records in the same file."""
    repo = UserRepository(db_path)
    for uid in ("U001", "U002", "U003"):
        repo.save(_make_user(uid))
    data = json.loads(db_path.read_text())
    assert set(data.keys()) == {"U001", "U002", "U003"}


def test_save_duplicate_raises_duplicate_user_error(db_path: Path) -> None:
    """Saving the same user_id twice must raise DuplicateUserError."""
    repo = UserRepository(db_path)
    repo.save(_make_user("U001"))
    with pytest.raises(DuplicateUserError, match="U001"):
        repo.save(_make_user("U001"))


def test_save_duplicate_does_not_overwrite_existing(db_path: Path) -> None:
    """After a DuplicateUserError the original record must remain unchanged."""
    repo = UserRepository(db_path)
    original = User("U001", "Original Name", "orig@example.com")
    repo.save(original)
    try:
        repo.save(User("U001", "Overwrite Attempt", "new@example.com"))
    except DuplicateUserError:
        pass
    data = json.loads(db_path.read_text())
    assert data["U001"]["name"] == "Original Name"


# ---------------------------------------------------------------------------
# UserRepository.count tests
# ---------------------------------------------------------------------------


def test_count_returns_zero_when_db_missing(db_path: Path) -> None:
    """count() must return 0 when the database file does not exist."""
    assert UserRepository(db_path).count() == 0


def test_count_returns_correct_number_after_saves(db_path: Path) -> None:
    """count() must reflect the exact number of saved records."""
    repo = UserRepository(db_path)
    for uid in ("U001", "U002"):
        repo.save(_make_user(uid))
    assert repo.count() == 2


# ---------------------------------------------------------------------------
# UserRepository.exists tests
# ---------------------------------------------------------------------------


def test_exists_returns_false_when_db_missing(db_path: Path) -> None:
    """exists() must return False when the database file does not exist."""
    assert UserRepository(db_path).exists("U001") is False


def test_exists_returns_true_after_save(db_path: Path) -> None:
    """exists() must return True for a user_id that was previously saved."""
    repo = UserRepository(db_path)
    repo.save(_make_user("U001"))
    assert repo.exists("U001") is True


def test_exists_returns_false_for_unknown_id(db_path: Path) -> None:
    """exists() must return False for a user_id not in the database."""
    repo = UserRepository(db_path)
    repo.save(_make_user("U001"))
    assert repo.exists("U999") is False
