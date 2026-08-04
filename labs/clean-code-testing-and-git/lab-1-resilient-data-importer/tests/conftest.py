"""Shared pytest fixtures for the Resilient Data Importer test suite.

Fixtures defined here are automatically available to every test module
without explicit imports, thanks to pytest's conftest.py discovery.
"""

import csv
from pathlib import Path

import pytest


@pytest.fixture
def valid_csv(tmp_path: Path) -> Path:
    """A well-formed CSV file containing three valid user rows.

    Args:
        tmp_path: pytest built-in temporary directory fixture.

    Returns:
        Path to the created CSV file.
    """
    file_path = tmp_path / "users.csv"
    rows = [
        {"user_id": "U001", "name": "Alice Johnson", "email": "alice@example.com"},
        {"user_id": "U002", "name": "Bob Smith", "email": "bob@example.com"},
        {"user_id": "U003", "name": "Carlos Rodriguez", "email": "carlos@example.com"},
    ]
    with file_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["user_id", "name", "email"])
        writer.writeheader()
        writer.writerows(rows)
    return file_path


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    """A temporary path for the JSON database (file does not exist yet).

    Args:
        tmp_path: pytest built-in temporary directory fixture.

    Returns:
        Path object pointing to a non-existent ``database.json``.
    """
    return tmp_path / "database.json"


@pytest.fixture
def single_row_csv(tmp_path: Path) -> Path:
    """A CSV file with exactly one valid row.

    Args:
        tmp_path: pytest built-in temporary directory fixture.

    Returns:
        Path to the created CSV file.
    """
    file_path = tmp_path / "single.csv"
    with file_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["user_id", "name", "email"])
        writer.writeheader()
        writer.writerow(
            {"user_id": "U001", "name": "Alice", "email": "alice@example.com"}
        )
    return file_path
