#!/usr/bin/env python3
"""Main entry point for the Resilient Data Importer.

Supports two modes of operation:

- **Interactive mode** (no CLI arguments): launches a console menu that lets
  the user import CSV files, add users manually, view/search/delete records,
  and switch the active database — all without typing commands.

- **CLI mode** (arguments provided): delegates directly to the existing
  ``import-users`` argument parser for scripted / automated use.

Usage:
    # Interactive mode
    python main.py

    # CLI mode (same as `import-users ...`)
    python main.py users.csv
    python main.py users.csv --db mydb.json --verbose
"""

import logging
import sys
from pathlib import Path

# Ensure `src/` is on the path when running main.py directly (without the
# package being installed into the active Python environment).
_SRC = Path(__file__).parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def _setup_logging(verbose: bool = False) -> None:
    """Configure root-level logging for the interactive session.

    Args:
        verbose: When ``True`` sets level to DEBUG, otherwise INFO.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=level,
        stream=sys.stdout,
    )


def _run_interactive() -> None:
    """Launch the interactive console menu.

    Uses the default ``database.json`` in the current working directory.
    The user can switch to a different database file from within the menu.
    """
    from importer.menu_handlers import MenuHandlers

    _setup_logging()
    db_path = Path("database.json")
    try:
        MenuHandlers(db_path).run()
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Goodbye!\n")
    except Exception as exc:
        logging.getLogger(__name__).error("Unexpected error: %s", exc, exc_info=True)
        sys.exit(1)


def _run_cli() -> None:
    """Delegate to the CLI argument parser (non-interactive mode)."""
    from importer.cli import _build_parser, _configure_logging, run_import

    parser = _build_parser()
    args = parser.parse_args()
    _configure_logging(args.verbose)

    summary = run_import(args.csv_file, args.db)
    if summary["errors"] > 0:
        sys.exit(1)


def main() -> None:
    """Detect mode and dispatch accordingly.

    If no positional arguments are passed on the command line, interactive
    mode is started.  Otherwise the standard CLI parser takes over.
    """
    # sys.argv[0] is the script name; interactive when nothing else is given.
    if len(sys.argv) == 1:
        _run_interactive()
    else:
        _run_cli()


if __name__ == "__main__":
    main()
