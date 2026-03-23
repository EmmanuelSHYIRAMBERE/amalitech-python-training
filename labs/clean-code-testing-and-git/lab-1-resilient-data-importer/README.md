<div align="center">
  <img src="https://amalitech.com/wp-content/uploads/elementor/thumbs/cropped-Logo-AmaliTech-2024_AmaliTech-1-1-qwx787mrcfwkgtwtxyaig0bixrwoxjaylsrbwor7ek.png" alt="AmaliTech Logo" width="280"/>
</div>
<br/>

# Lab 1 — Resilient Data Importer CLI

> A command-line tool that reliably imports user data from a CSV file into a
> JSON database, handling missing files, malformed rows, and duplicate entries
> with structured logging and a comprehensive pytest test suite.

---

## About

| | |
|---|---|
| **Trainee** | Emmanuel SHYIRAMBERE |
| **Module** | Clean Code, Testing and Git |
| **Lab** | Lab 1 — Resilient Data Importer CLI |
| **Python** | 3.11+ |

---

## Project Structure

```
lab-1-resilient-data-importer/
├── src/
│   └── importer/
│       ├── __init__.py
│       ├── cli.py          # CLI entry point (argparse) + run_import pipeline
│       ├── exceptions.py   # Custom exception hierarchy
│       ├── models.py       # User dataclass
│       ├── parser.py       # CSV parsing (Single Responsibility)
│       ├── validator.py    # Field validation (Single Responsibility)
│       └── repository.py   # JSON storage + _open_db context manager
├── tests/
│   ├── conftest.py         # Shared fixtures (valid_csv, db_path, etc.)
│   ├── test_models.py      # User dataclass + exception hierarchy tests
│   ├── test_parser.py      # CSV parser tests (parametrize, edge cases)
│   ├── test_validator.py   # Validator tests (parametrize, invalid emails)
│   ├── test_repository.py  # Repository + context manager tests
│   └── test_cli.py         # Integration + mocked unit tests for CLI
├── sample_data/
│   ├── users.csv               # Clean sample data
│   └── users_with_errors.csv   # Sample with intentional errors
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone and navigate

```bash
git clone <your-repo-url>
cd lab-1-resilient-data-importer
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install the package and dependencies

```bash
pip install -e .
pip install -r requirements.txt
```

### 4. Install pre-commit hooks

```bash
pre-commit install
```

The hooks will now run **Black**, **ruff**, and **mypy** automatically before
every `git commit`.

---

## Usage

### Basic import

```bash
import-users sample_data/users.csv
```

### Custom database path

```bash
import-users sample_data/users.csv --db my_database.json
```

### Verbose (DEBUG) logging

```bash
import-users sample_data/users.csv -v
```

### Test with intentional errors

```bash
import-users sample_data/users_with_errors.csv -v
```

Expected output (example):

```
2024-01-01 12:00:00 [INFO    ] importer.cli: ✅ Imported: Frank Ocean (U006)
2024-01-01 12:00:00 [INFO    ] importer.cli: ✅ Imported: Grace Hopper (U007)
2024-01-01 12:00:00 [WARNING ] importer.cli: Validation failed — skipping row: user_id is empty ...
2024-01-01 12:00:00 [WARNING ] importer.cli: Validation failed — skipping row: Invalid email ...
2024-01-01 12:00:00 [WARNING ] importer.cli: Duplicate entry — skipping: User 'U006' already exists ...
2024-01-01 12:00:00 [INFO    ] importer.cli: ✅ Imported: Valid Again (U010)
2024-01-01 12:00:00 [INFO    ] importer.cli: Import complete — imported: 3 | skipped: 3 | errors: 0
```

### Exit codes

| Code | Meaning |
|------|---------|
| `0`  | Import completed (full or partial success) |
| `1`  | Unrecoverable error (e.g. file not found, unreadable CSV) |

---

## Running Tests

### Run the full test suite

```bash
pytest
```

### Run with coverage report

```bash
coverage run -m pytest
coverage report
```

### Generate HTML coverage report

```bash
coverage run -m pytest
coverage html
# Open htmlcov/index.html in your browser
```

### Run a specific test file

```bash
pytest tests/test_parser.py -v
```

---

## Architecture & Design Decisions

### SOLID Principles Applied

| Principle | Implementation |
|-----------|---------------|
| **S** — Single Responsibility | `parser.py` only reads CSV; `validator.py` only validates; `repository.py` only persists |
| **O** — Open/Closed | New storage backends can be added without modifying `cli.py` |
| **D** — Dependency Inversion | `run_import` depends on `UserRepository` (concrete but swappable via mocking) |

### Exception Hierarchy

```
ImporterError (base)
├── FileFormatError   — missing/unreadable/malformed CSV
├── DuplicateUserError — user_id already in database
└── ValidationError   — empty fields, invalid email
```

### Context Manager (`_open_db`)

The `_open_db` context manager in `repository.py` guarantees that the JSON
database is **always written back to disk** — even if an exception occurs
mid-operation — preventing partial writes and data loss.

### try/except/else/finally in `run_import`

```python
try:
    validate_user(user)
    repo.save(user)
except ValidationError:
    summary["skipped"] += 1   # expected, recoverable
except DuplicateUserError:
    summary["skipped"] += 1   # expected, recoverable
except Exception:
    summary["errors"] += 1    # unexpected, logged
else:
    summary["imported"] += 1  # only on full success
finally:
    logger.debug("Finished processing: %s", user.user_id)  # always runs
```

---

## Git Flow Workflow

```
main ──────────────────────────────────────── v1.0
       \                                    /
        develop ──────────────────────────
          \── feature/exceptions ──/
          \── feature/models ──/
          \── feature/csv-parser ──/
          \── feature/validator ──/
          \── feature/repository ──/
          \── feature/cli ──/
          \── feature/tests ──/
```

### Branch commands

```bash
# Start a new feature
git checkout develop
git checkout -b feature/csv-parser

# Finish and merge (via PR on GitHub)
git push origin feature/csv-parser
# Open PR: feature/csv-parser → develop

# Release
git checkout main
git merge develop
git tag v1.0.0
```

---

## Pre-commit Hooks

Configured in `.pre-commit-config.yaml`:

| Hook | Purpose |
|------|---------|
| `black` | Auto-formats code to PEP 8 style |
| `ruff` | Lints for errors, unused imports, style issues |
| `mypy` | Static type checking with `--strict` |

Run manually at any time:

```bash
pre-commit run --all-files
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `pytest` | Test framework |
| `pytest-mock` | Mocking support (`mocker` fixture) |
| `coverage` | Test coverage measurement |
| `black` | Code formatter |
| `ruff` | Fast linter |
| `mypy` | Static type checker |
| `pre-commit` | Git hook manager |

---

<div align="center">
  <sub>Built with Python 3.11+ · AmaliTech Training Program · Clean Code, Testing and Git Module</sub>
</div>
