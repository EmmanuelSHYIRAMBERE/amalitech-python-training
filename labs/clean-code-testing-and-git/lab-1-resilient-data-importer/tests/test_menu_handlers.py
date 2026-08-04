"""Tests for the interactive menu handlers (importer.menu_handlers).

All ``input()`` calls are patched via ``builtins.input`` so tests run
non-interactively.  The repository is exercised against real tmp files
to keep integration coverage high.
"""

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from importer.menu_handlers import MenuHandlers, _menu, _prompt, _yn

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _make_db(tmp_path: Path, records: dict[str, Any] | None = None) -> Path:
    """Write a JSON database file and return its path."""
    db = tmp_path / "database.json"
    db.write_text(json.dumps(records or {}), encoding="utf-8")
    return db


# ---------------------------------------------------------------------------
# Pure helper function tests
# ---------------------------------------------------------------------------


def test_prompt_returns_valid_input() -> None:
    """_prompt must return the first input that passes the validator."""
    with patch("builtins.input", side_effect=["", "hello"]):
        result = _prompt("label: ", lambda x: bool(x), "bad")
    assert result == "hello"


def test_prompt_no_validator_accepts_any_input() -> None:
    """_prompt with no validator must accept the first value entered."""
    with patch("builtins.input", return_value="anything"):
        assert _prompt("label: ") == "anything"


def test_yn_returns_true_for_y() -> None:
    with patch("builtins.input", return_value="y"):
        assert _yn("question") is True


def test_yn_returns_false_for_n() -> None:
    with patch("builtins.input", return_value="n"):
        assert _yn("question") is False


def test_yn_retries_on_invalid_then_accepts() -> None:
    with patch("builtins.input", side_effect=["x", "y"]):
        assert _yn("question") is True


def test_menu_returns_integer_choice() -> None:
    with patch("builtins.input", return_value="2"):
        assert _menu(["A", "B", "C"]) == 2


def test_menu_returns_zero_for_back() -> None:
    with patch("builtins.input", return_value="0"):
        assert _menu(["A"]) == 0


def test_menu_retries_on_out_of_range() -> None:
    with patch("builtins.input", side_effect=["9", "1"]):
        assert _menu(["A"]) == 1


# ---------------------------------------------------------------------------
# MenuHandlers._import_csv
# ---------------------------------------------------------------------------


def test_import_csv_success(
    valid_csv: Path, db_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Choosing option 1 with a valid CSV must print a success summary."""
    handler = MenuHandlers(db_path)
    inputs = [
        str(valid_csv),  # CSV path
        "n",  # verbose?
    ]
    with patch("builtins.input", side_effect=inputs):
        handler._import_csv()

    out = capsys.readouterr().out
    assert "Imported" in out
    assert "3" in out


def test_import_csv_missing_file_shows_error(
    tmp_path: Path, db_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A missing CSV path must show errors=1 in the summary."""
    handler = MenuHandlers(db_path)
    inputs = [str(tmp_path / "ghost.csv"), "n"]
    with patch("builtins.input", side_effect=inputs):
        handler._import_csv()

    out = capsys.readouterr().out
    assert "Errors" in out


# ---------------------------------------------------------------------------
# MenuHandlers._add_user_manually
# ---------------------------------------------------------------------------


def test_add_user_manually_saves_valid_user(
    db_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Entering valid fields must persist the user and print a success message."""
    handler = MenuHandlers(db_path)
    inputs = ["U001", "Alice Johnson", "alice@example.com"]
    with patch("builtins.input", side_effect=inputs):
        handler._add_user_manually()

    assert handler._repo.exists("U001")
    assert "added successfully" in capsys.readouterr().out


def test_add_user_manually_invalid_email_reprompts_then_succeeds(
    db_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An invalid email must re-prompt the email field, not abort."""
    handler = MenuHandlers(db_path)
    # user_id, name, bad email, good email
    inputs = ["U001", "Alice", "not-valid", "alice@example.com"]
    with patch("builtins.input", side_effect=inputs):
        handler._add_user_manually()

    assert handler._repo.exists("U001")
    out = capsys.readouterr().out
    assert "Invalid email" in out
    assert "added successfully" in out


def test_add_user_manually_duplicate_reprompts_id_then_succeeds(
    db_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A duplicate user_id must re-prompt for a new ID, not abort."""
    handler = MenuHandlers(db_path)
    # Pre-seed U001
    with patch("builtins.input", side_effect=["U001", "Alice", "alice@example.com"]):
        handler._add_user_manually()
    capsys.readouterr()

    # user_id=U001 (duplicate) → new user_id prompt → U002
    # then the loop restarts: email prompt again → bob@example.com → save OK
    inputs = ["U001", "Bob", "bob@example.com", "U002", "bob@example.com"]
    with patch("builtins.input", side_effect=inputs):
        handler._add_user_manually()

    assert handler._repo.exists("U002")
    out = capsys.readouterr().out
    assert "already exists" in out
    assert "added successfully" in out


def test_add_user_manually_invalid_email_shows_error(
    db_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The invalid-email error message must be printed before re-prompting."""
    handler = MenuHandlers(db_path)
    # bad email first, then valid
    inputs = ["U001", "Alice", "not-valid", "alice@example.com"]
    with patch("builtins.input", side_effect=inputs):
        handler._add_user_manually()
    assert "Invalid email" in capsys.readouterr().out


def test_add_user_manually_duplicate_shows_error(
    db_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The duplicate-ID error message must be printed before re-prompting."""
    handler = MenuHandlers(db_path)
    with patch("builtins.input", side_effect=["U001", "Alice", "alice@example.com"]):
        handler._add_user_manually()
    capsys.readouterr()

    # U001 duplicate → re-prompt user_id → U002, then re-prompt email → success
    inputs = ["U001", "Bob", "bob@example.com", "U002", "bob@example.com"]
    with patch("builtins.input", side_effect=inputs):
        handler._add_user_manually()
    assert "already exists" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# MenuHandlers._view_all_users
# ---------------------------------------------------------------------------


def test_view_all_users_shows_records(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """_view_all_users must print each stored user's ID and name."""
    db = _make_db(
        tmp_path,
        {
            "U001": {
                "user_id": "U001",
                "name": "Alice",
                "email": "a@a.com",
                "imported_at": "2024-01-01T00:00:00",
            },
            "U002": {
                "user_id": "U002",
                "name": "Bob",
                "email": "b@b.com",
                "imported_at": "2024-01-01T00:00:00",
            },
        },
    )
    MenuHandlers(db)._view_all_users()
    out = capsys.readouterr().out
    assert "U001" in out
    assert "Alice" in out
    assert "U002" in out
    assert "Total: 2" in out


def test_view_all_users_empty_db(
    db_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An empty database must print the 'empty' message."""
    db_path.write_text("{}", encoding="utf-8")
    MenuHandlers(db_path)._view_all_users()
    assert "empty" in capsys.readouterr().out


def test_view_all_users_no_db_file(
    db_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A missing database file must print the 'No database found' message."""
    MenuHandlers(db_path)._view_all_users()
    assert "No database found" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# MenuHandlers._search_user
# ---------------------------------------------------------------------------


def test_search_user_found(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Searching an existing user_id must print their details."""
    db = _make_db(
        tmp_path,
        {
            "U001": {
                "user_id": "U001",
                "name": "Alice",
                "email": "a@a.com",
                "imported_at": "2024-01-01T00:00:00",
            }
        },
    )
    with patch("builtins.input", return_value="U001"):
        MenuHandlers(db)._search_user()

    out = capsys.readouterr().out
    assert "Alice" in out
    assert "a@a.com" in out


def test_search_user_not_found(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Searching a non-existent user_id must print 'not found'."""
    db = _make_db(tmp_path, {})
    with patch("builtins.input", return_value="U999"):
        MenuHandlers(db)._search_user()

    assert "not found" in capsys.readouterr().out


def test_search_user_no_db(db_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Searching when no database exists must print 'No database found'."""
    with patch("builtins.input", return_value="U001"):
        MenuHandlers(db_path)._search_user()

    assert "No database found" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# MenuHandlers._delete_user
# ---------------------------------------------------------------------------


def test_delete_user_confirmed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Confirming deletion must remove the record from the database."""
    db = _make_db(
        tmp_path,
        {
            "U001": {
                "user_id": "U001",
                "name": "Alice",
                "email": "a@a.com",
                "imported_at": "",
            }
        },
    )
    handler = MenuHandlers(db)
    with patch("builtins.input", side_effect=["U001", "y"]):
        handler._delete_user()

    assert not handler._repo.exists("U001")
    assert "deleted" in capsys.readouterr().out


def test_delete_user_cancelled(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Cancelling deletion must leave the record intact."""
    db = _make_db(
        tmp_path,
        {
            "U001": {
                "user_id": "U001",
                "name": "Alice",
                "email": "a@a.com",
                "imported_at": "",
            }
        },
    )
    handler = MenuHandlers(db)
    with patch("builtins.input", side_effect=["U001", "n"]):
        handler._delete_user()

    assert handler._repo.exists("U001")
    assert "cancelled" in capsys.readouterr().out


def test_delete_user_not_found(
    tmp_path: Path, db_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Deleting a non-existent user_id must print 'not found'."""
    db_path.write_text("{}", encoding="utf-8")
    with patch("builtins.input", return_value="U999"):
        MenuHandlers(db_path)._delete_user()

    assert "not found" in capsys.readouterr().out


def test_delete_user_no_db(db_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Deleting when no database exists must print 'No database found'."""
    with patch("builtins.input", return_value="U001"):
        MenuHandlers(db_path)._delete_user()

    assert "No database found" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# MenuHandlers._change_database
# ---------------------------------------------------------------------------


def test_change_database_updates_path(
    db_path: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Entering a new path must update the handler's internal db_path."""
    handler = MenuHandlers(db_path)
    new_db = tmp_path / "new.json"
    with patch("builtins.input", return_value=str(new_db)):
        handler._change_database()

    assert handler._db_path == new_db
    assert "switched" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# MenuHandlers.run — top-level loop
# ---------------------------------------------------------------------------


def test_run_exits_on_choice_0(
    db_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Choosing 0 at the main menu must exit the loop cleanly."""
    db_path.write_text("{}", encoding="utf-8")
    with patch("builtins.input", return_value="0"):
        MenuHandlers(db_path).run()

    assert "Goodbye" in capsys.readouterr().out


def test_run_dispatches_view_all_then_exits(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Choosing 3 (view all) then 0 (exit) must call _view_all_users."""
    db = _make_db(tmp_path, {})
    # choice=3 → view all; then Enter to continue; then choice=0 → exit
    with patch("builtins.input", side_effect=["3", "", "0"]):
        MenuHandlers(db).run()

    out = capsys.readouterr().out
    assert "Goodbye" in out
