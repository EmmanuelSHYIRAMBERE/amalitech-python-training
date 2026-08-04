"""CLI entry point for the Resilient Data Importer.

Provides the ``main`` function (registered as the ``import-users`` console
script) and the ``run_import`` orchestration function that wires together
the parser, validator, and repository components.

Usage:
    import-users path/to/users.csv
    import-users path/to/users.csv --db path/to/database.json --verbose
"""

import argparse
import logging
import sys
from pathlib import Path

from importer.exceptions import DuplicateUserError, FileFormatError, ValidationError
from importer.parser import parse_csv
from importer.repository import UserRepository
from importer.validator import validate_user

logger = logging.getLogger(__name__)


def _configure_logging(verbose: bool) -> None:
    """Configure root logger level and format.

    Args:
        verbose: When ``True``, sets level to DEBUG; otherwise INFO.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=level,
        stream=sys.stdout,
    )


def run_import(csv_path: Path, db_path: Path) -> dict[str, int]:
    """Orchestrate the full CSV → JSON import pipeline.

    Parses the CSV, validates each row, and persists valid records via the
    repository.  Uses ``try/except/else/finally`` to handle every error
    class distinctly and guarantee that a summary is always returned.

    Args:
        csv_path: Path to the source CSV file.
        db_path: Path to the target JSON database file.

    Returns:
        A summary dict with integer counts for the keys:
        ``"imported"``, ``"skipped"``, and ``"errors"``.

    Example:
        >>> summary = run_import(Path("users.csv"), Path("db.json"))
        >>> print(summary)
        {'imported': 3, 'skipped': 0, 'errors': 0}
    """
    repo = UserRepository(db_path)
    summary: dict[str, int] = {"imported": 0, "skipped": 0, "errors": 0}

    # --- Parse phase ---
    try:
        users = list(parse_csv(csv_path))
    except FileFormatError as exc:
        logger.error("Failed to open or parse CSV: %s", exc)
        summary["errors"] += 1
        return summary

    # --- Validate + persist phase ---
    for user in users:
        try:
            validate_user(user)
            repo.save(user)

        except ValidationError as exc:
            logger.warning("Validation failed — skipping row: %s", exc)
            summary["skipped"] += 1

        except DuplicateUserError as exc:
            logger.warning("Duplicate entry — skipping: %s", exc)
            summary["skipped"] += 1

        except Exception as exc:  # noqa: BLE001 — catch-all safety net
            logger.error("Unexpected error processing user '%s': %s", user.user_id, exc)
            summary["errors"] += 1

        else:
            # Only reached when no exception was raised above.
            logger.info("Imported: %s (%s)", user.name, user.user_id)
            summary["imported"] += 1

        finally:
            # Always executed — useful for audit/debug tracing.
            logger.debug("Finished processing record: '%s'", user.user_id)

    logger.info(
        "Import complete — imported: %d | skipped: %d | errors: %d",
        summary["imported"],
        summary["skipped"],
        summary["errors"],
    )
    return summary


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser.

    Returns:
        Configured ``ArgumentParser`` instance.
    """
    parser = argparse.ArgumentParser(
        prog="import-users",
        description=(
            "Resilient Data Importer — imports user records from a CSV file "
            "into a JSON database, handling duplicates and malformed rows."
        ),
    )
    parser.add_argument(
        "csv_file",
        type=Path,
        help="Path to the source CSV file (must have user_id, name, email columns).",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("database.json"),
        metavar="PATH",
        help="Path to the JSON database file (default: database.json).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging output.",
    )
    return parser


def main() -> None:
    """Parse CLI arguments and run the importer.

    Exits with code ``1`` if any unrecoverable errors occurred during the
    import, or ``0`` on full or partial success.
    """
    args = _build_parser().parse_args()
    _configure_logging(args.verbose)

    summary = run_import(args.csv_file, args.db)

    if summary["errors"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
