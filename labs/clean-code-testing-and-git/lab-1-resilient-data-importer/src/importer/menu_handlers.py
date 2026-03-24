"""Interactive menu handlers for the Resilient Data Importer.

Provides the ``MenuHandlers`` class which drives a console-based interactive
session.  Each public method maps to one menu screen.  All I/O goes through
``_prompt`` / ``_prompt_path`` helpers so the rest of the logic stays clean
and testable.
"""

import json
import logging
import os
from collections.abc import Callable
from pathlib import Path

from importer.cli import run_import
from importer.exceptions import DuplicateUserError, ValidationError
from importer.models import User
from importer.repository import UserRepository
from importer.validator import validate_user

logger = logging.getLogger(__name__)

# ── visual helpers ────────────────────────────────────────────────────────────
_SEP = "=" * 55
_DIV = "-" * 55


def _clear() -> None:
    """Clear the terminal screen (cross-platform)."""
    os.system("cls" if os.name == "nt" else "clear")


def _header(title: str) -> None:
    """Print a section header."""
    print(f"\n{_SEP}")
    print(f"  {title}")
    print(_SEP)


def _prompt(
    label: str,
    validator: Callable[[str], bool] | None = None,
    error: str = "Invalid input.",
) -> str:
    """Prompt the user until a valid value is entered.

    Args:
        label: The prompt string shown to the user.
        validator: Optional callable that returns ``True`` for valid input.
            When ``None`` any non-empty string is accepted.
        error: Message printed when validation fails.

    Returns:
        The validated, stripped input string.
    """
    while True:
        value = input(f"  {label}").strip()
        if validator is None or validator(value):
            return value
        print(f"  [!] {error}")


def _prompt_path(label: str) -> Path:
    """Prompt for a file-system path and return it as a ``Path``.

    Args:
        label: The prompt string shown to the user.

    Returns:
        A ``Path`` object for the entered string.
    """
    raw = _prompt(label)
    return Path(raw)


def _yn(label: str) -> bool:
    """Prompt for a yes/no answer.

    Args:
        label: The question to display.

    Returns:
        ``True`` for 'y', ``False`` for 'n'.
    """
    answer = _prompt(f"{label} (y/n): ", lambda x: x.lower() in ("y", "n"))
    return answer.lower() == "y"


def _menu(options: list[str]) -> int:
    """Print a numbered menu and return the validated integer choice.

    Args:
        options: List of option labels (1-indexed in display).

    Returns:
        Integer choice between 0 (back/exit) and ``len(options)``.
    """
    print()
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    print("  0. Back / Exit")
    print(_DIV)
    raw = _prompt(
        "Enter choice: ",
        lambda x: x.isdigit() and 0 <= int(x) <= len(options),
        f"Enter a number between 0 and {len(options)}.",
    )
    return int(raw)


# ── main handler class ────────────────────────────────────────────────────────


class MenuHandlers:
    """Drives the interactive console session for the Data Importer.

    Args:
        db_path: Path to the JSON database file used for all operations.

    Example:
        >>> from pathlib import Path
        >>> MenuHandlers(Path("database.json")).run()
    """

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._repo = UserRepository(db_path)

    # ── top-level loop ────────────────────────────────────────────────────────

    def run(self) -> None:
        """Start the main interactive menu loop."""
        while True:
            _clear()
            _header("Resilient Data Importer — Interactive Mode")
            print(f"  Database : {self._db_path}")
            print(f"  Records  : {self._repo.count()}")

            choice = _menu(
                [
                    "Import from CSV file",
                    "Add a single user manually",
                    "View all users",
                    "Search user by ID",
                    "Delete a user",
                    "Change database file",
                ]
            )

            if choice == 0:
                print("\n  Goodbye!\n")
                break
            elif choice == 1:
                self._import_csv()
            elif choice == 2:
                self._add_user_manually()
            elif choice == 3:
                self._view_all_users()
            elif choice == 4:
                self._search_user()
            elif choice == 5:
                self._delete_user()
            elif choice == 6:
                self._change_database()

            input("\n  Press Enter to continue...")

    # ── sub-menus / actions ───────────────────────────────────────────────────

    def _import_csv(self) -> None:
        """Prompt for a CSV path and run the full import pipeline."""
        _header("Import from CSV File")
        print("  The CSV must have columns: user_id, name, email")
        print()

        csv_path = _prompt_path("CSV file path: ")

        verbose = _yn("Enable verbose (DEBUG) logging?")

        # Configure logging level for this run only.
        level = logging.DEBUG if verbose else logging.INFO
        logging.getLogger().setLevel(level)

        print()
        summary = run_import(csv_path, self._db_path)

        print()
        print(_DIV)
        print(f"  Imported : {summary['imported']}")
        print(f"  Skipped  : {summary['skipped']}")
        print(f"  Errors   : {summary['errors']}")
        print(_DIV)

    def _add_user_manually(self) -> None:
        """Prompt for individual fields and save a single user record.

        Re-prompts the email field on validation failure and re-prompts the
        user_id on a duplicate, so the user never has to restart from scratch.
        """
        _header("Add User Manually")

        user_id = _prompt(
            "User ID   : ",
            lambda x: bool(x),
            "User ID cannot be empty.",
        )
        name = _prompt(
            "Full Name : ",
            lambda x: bool(x.strip()),
            "Name cannot be empty.",
        )

        while True:
            email = _prompt(
                "Email     : ",
                lambda x: bool(x.strip()),
                "Email cannot be empty.",
            )
            user = User(user_id=user_id, name=name, email=email)
            try:
                validate_user(user)
            except ValidationError as exc:
                print(f"\n  [!] {exc}")
                print("  Please enter a valid email address.")
                continue  # re-prompt email only

            try:
                self._repo.save(user)
                print(f"\n  [OK] User '{name}' ({user_id}) added successfully.")
            except DuplicateUserError as exc:
                print(f"\n  [!] {exc}")
                user_id = _prompt(
                    "Enter a different User ID: ",
                    lambda x: bool(x),
                    "User ID cannot be empty.",
                )
                continue  # retry the whole save with the new ID
            break

    def _view_all_users(self) -> None:
        """Display all users currently stored in the database."""
        _header("All Users")

        if not self._db_path.exists():
            print("  No database found. Import some users first.")
            return

        with self._db_path.open(encoding="utf-8") as fh:
            data: dict[str, dict[str, str]] = json.load(fh)

        if not data:
            print("  Database is empty.")
            return

        print(f"  {'ID':<12} {'Name':<25} {'Email':<30} {'Imported At'}")
        print(_DIV)
        for record in data.values():
            imported = record.get("imported_at", "")[:19].replace("T", " ")
            print(
                f"  {record['user_id']:<12} "
                f"{record['name']:<25} "
                f"{record['email']:<30} "
                f"{imported}"
            )
        print(_DIV)
        print(f"  Total: {len(data)} user(s)")

    def _search_user(self) -> None:
        """Look up and display a single user by their user_id."""
        _header("Search User by ID")

        user_id = _prompt("User ID: ", lambda x: bool(x), "ID cannot be empty.")

        if not self._db_path.exists():
            print("  No database found.")
            return

        with self._db_path.open(encoding="utf-8") as fh:
            data: dict[str, dict[str, str]] = json.load(fh)

        record = data.get(user_id)
        if record is None:
            print(f"\n  [!] User '{user_id}' not found.")
            return

        imported = record.get("imported_at", "")[:19].replace("T", " ")
        print()
        print(f"  User ID     : {record['user_id']}")
        print(f"  Name        : {record['name']}")
        print(f"  Email       : {record['email']}")
        print(f"  Imported At : {imported}")

    def _delete_user(self) -> None:
        """Remove a user record from the database by user_id."""
        _header("Delete User")

        user_id = _prompt(
            "User ID to delete: ", lambda x: bool(x), "ID cannot be empty."
        )

        if not self._db_path.exists():
            print("  No database found.")
            return

        with self._db_path.open(encoding="utf-8") as fh:
            data: dict[str, dict[str, str]] = json.load(fh)

        if user_id not in data:
            print(f"\n  [!] User '{user_id}' not found.")
            return

        record = data[user_id]
        print(f"\n  Found: {record['name']} ({record['email']})")

        if _yn("  Confirm deletion?"):
            del data[user_id]
            with self._db_path.open("w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            print(f"\n  [OK] User '{user_id}' deleted.")
            logger.info("Deleted user '%s'", user_id)
        else:
            print("  Deletion cancelled.")

    def _change_database(self) -> None:
        """Switch the active database file path."""
        _header("Change Database File")
        print(f"  Current: {self._db_path}")
        print()

        new_path = _prompt_path("New database path: ")
        self._db_path = new_path
        self._repo = UserRepository(new_path)
        print(f"\n  [OK] Database switched to: {new_path}")
        logger.info("Database path changed to '%s'", new_path)


def _interactive_entry() -> None:
    """Console-script entry point for interactive mode.

    Registered as ``import-users-interactive`` in ``pyproject.toml``.
    Starts the menu with the default ``database.json`` in the current
    working directory.  The user can switch databases from within the menu.
    """
    import sys

    logging.basicConfig(
        format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
        stream=sys.stdout,
    )
    try:
        MenuHandlers(Path("database.json")).run()
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Goodbye!\n")
    except Exception as exc:
        logger.error("Unexpected error: %s", exc, exc_info=True)
        sys.exit(1)
