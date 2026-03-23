"""Tests for the CLI orchestration layer (importer.cli).

Covers: full happy-path integration, bad CSV, validation failures,
duplicate skipping, mocked repository, and the main() exit-code behaviour.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from importer.cli import _build_parser, run_import
from importer.exceptions import DuplicateUserError

# ---------------------------------------------------------------------------
# run_import — integration tests (real components, tmp files)
# ---------------------------------------------------------------------------


def test_run_import_success_imports_all_rows(valid_csv: Path, db_path: Path) -> None:
    """All three valid rows must be imported with zero skips and errors."""
    summary = run_import(valid_csv, db_path)
    assert summary == {"imported": 3, "skipped": 0, "errors": 0}


def test_run_import_creates_database_file(valid_csv: Path, db_path: Path) -> None:
    """After a successful import the JSON database file must exist."""
    run_import(valid_csv, db_path)
    assert db_path.exists()


def test_run_import_missing_csv_returns_error(tmp_path: Path, db_path: Path) -> None:
    """A non-existent CSV path must result in errors=1, imported=0."""
    summary = run_import(tmp_path / "ghost.csv", db_path)
    assert summary["errors"] == 1
    assert summary["imported"] == 0


def test_run_import_skips_invalid_email_rows(tmp_path: Path, db_path: Path) -> None:
    """Rows with invalid emails must be counted as skipped, not errors."""
    f = tmp_path / "bad_email.csv"
    f.write_text("user_id,name,email\nU001,Alice,not-valid\n", encoding="utf-8")
    summary = run_import(f, db_path)
    assert summary["skipped"] == 1
    assert summary["imported"] == 0
    assert summary["errors"] == 0


def test_run_import_skips_empty_user_id_rows(tmp_path: Path, db_path: Path) -> None:
    """Rows with an empty user_id must be skipped."""
    f = tmp_path / "empty_id.csv"
    f.write_text("user_id,name,email\n,Alice,alice@example.com\n", encoding="utf-8")
    summary = run_import(f, db_path)
    assert summary["skipped"] == 1


def test_run_import_skips_duplicate_on_second_run(
    valid_csv: Path, db_path: Path
) -> None:
    """Running the same CSV twice must skip all rows on the second run."""
    run_import(valid_csv, db_path)
    summary = run_import(valid_csv, db_path)
    assert summary["skipped"] == 3
    assert summary["imported"] == 0


def test_run_import_mixed_valid_and_invalid(tmp_path: Path, db_path: Path) -> None:
    """A file with 2 valid and 1 invalid row must import 2 and skip 1."""
    f = tmp_path / "mixed.csv"
    f.write_text(
        "user_id,name,email\n"
        "U001,Alice,alice@example.com\n"
        "U002,Bob,not-an-email\n"
        "U003,Carlos,carlos@example.com\n",
        encoding="utf-8",
    )
    summary = run_import(f, db_path)
    assert summary["imported"] == 2
    assert summary["skipped"] == 1
    assert summary["errors"] == 0


# ---------------------------------------------------------------------------
# run_import — mocked repository (unit isolation)
# ---------------------------------------------------------------------------


def test_run_import_calls_repo_save_for_each_valid_row(
    valid_csv: Path, db_path: Path, mocker: MagicMock
) -> None:
    """repo.save must be called exactly once per valid row."""
    mock_repo_cls = mocker.patch("importer.cli.UserRepository")
    mock_instance = MagicMock()
    mock_repo_cls.return_value = mock_instance

    run_import(valid_csv, db_path)

    assert mock_instance.save.call_count == 3


def test_run_import_counts_skipped_when_repo_raises_duplicate(
    valid_csv: Path, db_path: Path, mocker: MagicMock
) -> None:
    """DuplicateUserError from the repo must increment skipped, not errors."""
    mock_repo_cls = mocker.patch("importer.cli.UserRepository")
    mock_instance = MagicMock()
    mock_instance.save.side_effect = DuplicateUserError("U001")
    mock_repo_cls.return_value = mock_instance

    summary = run_import(valid_csv, db_path)

    assert summary["skipped"] == 3
    assert summary["errors"] == 0


def test_run_import_counts_errors_on_unexpected_exception(
    valid_csv: Path, db_path: Path, mocker: MagicMock
) -> None:
    """An unexpected exception from repo.save must increment errors."""
    mock_repo_cls = mocker.patch("importer.cli.UserRepository")
    mock_instance = MagicMock()
    mock_instance.save.side_effect = RuntimeError("disk full")
    mock_repo_cls.return_value = mock_instance

    summary = run_import(valid_csv, db_path)

    assert summary["errors"] == 3
    assert summary["imported"] == 0


# ---------------------------------------------------------------------------
# _build_parser tests
# ---------------------------------------------------------------------------


def test_build_parser_defaults(tmp_path: Path) -> None:
    """Default --db value must be 'database.json' and verbose must be False."""
    parser = _build_parser()
    args = parser.parse_args([str(tmp_path / "users.csv")])
    assert args.db == Path("database.json")
    assert args.verbose is False


def test_build_parser_accepts_custom_db(tmp_path: Path) -> None:
    """--db flag must override the default database path."""
    parser = _build_parser()
    args = parser.parse_args([str(tmp_path / "u.csv"), "--db", "custom.json"])
    assert args.db == Path("custom.json")


def test_build_parser_verbose_flag(tmp_path: Path) -> None:
    """-v flag must set verbose to True."""
    parser = _build_parser()
    args = parser.parse_args([str(tmp_path / "u.csv"), "-v"])
    assert args.verbose is True


# ---------------------------------------------------------------------------
# main() exit-code tests
# ---------------------------------------------------------------------------


def test_main_exits_with_code_1_on_error(tmp_path: Path) -> None:
    """main() must call sys.exit(1) when the CSV file does not exist."""
    with patch("sys.argv", ["import-users", str(tmp_path / "missing.csv")]):
        with pytest.raises(SystemExit) as exc_info:
            from importer.cli import main

            main()
        assert exc_info.value.code == 1


def test_main_exits_cleanly_on_success(valid_csv: Path, db_path: Path) -> None:
    """main() must not raise SystemExit when the import succeeds."""
    with patch("sys.argv", ["import-users", str(valid_csv), "--db", str(db_path)]):
        from importer.cli import main

        main()  # must not raise
