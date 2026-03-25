# Lab 2: TDD-based Weather API Service Stub

A mock Weather API service built using strict **Test-Driven Development (TDD)**, clean architecture, and SOLID principles.

---

## Architecture

```
src/weather/
├── exceptions.py      # WeatherServiceError, InvalidAPIKeyError, CityNotFoundError
├── models.py          # WeatherRequest, WeatherResponse (dataclasses)
├── provider.py        # Abstract WeatherProvider (Dependency Inversion)
├── mock_provider.py   # MockWeatherProvider — deterministic test data
└── service.py         # WeatherService — public API, logging, validation
```

The `WeatherService` depends on the abstract `WeatherProvider` interface, not any concrete implementation. Swapping the mock for a real OpenWeatherMap provider requires zero changes to `WeatherService`.

---

## TDD Workflow

Every feature followed the **Red → Green → Refactor** cycle:

| Cycle | Red (failing test) | Green (min code) | Refactor |
|---|---|---|---|
| 1 | `test_models.py` — WeatherRequest/Response fields | `models.py` dataclasses | Added docstrings |
| 2 | `test_exceptions.py` — exception hierarchy | `exceptions.py` with base class | Tightened messages |
| 3 | `test_mock_provider.py` — known cities, bad key, unknown city | `provider.py` ABC + `mock_provider.py` | Extracted `_MOCK_DATA` constant |
| 4 | `test_service.py` — happy path, errors, logging, DI | `service.py` with structured logging | Extracted validation, re-raise pattern |

The commit history reflects each cycle: a `test:` commit (red) followed by a `feat:` commit (green).

---

## SOLID Principles Applied

- **S** — Each class has one responsibility: `MockWeatherProvider` only provides data; `WeatherService` only orchestrates.
- **O** — `WeatherService` is open for extension (new providers) without modification.
- **L** — `MockWeatherProvider` is a drop-in replacement for any future `WeatherProvider`.
- **I** — `WeatherProvider` exposes only the `fetch` method — nothing more.
- **D** — `WeatherService` depends on the `WeatherProvider` abstraction, injected at construction.

---

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
pip install -e .
```

## Run Tests

```bash
pytest -v
```

## Coverage Report

```bash
python -m coverage run -m pytest
python -m coverage report
```

```
Name                           Stmts   Miss  Cover
--------------------------------------------------
src\weather\__init__.py            6      0   100%
src\weather\exceptions.py          7      0   100%
src\weather\mock_provider.py      13      0   100%
src\weather\models.py              5      0   100%
src\weather\provider.py            5      0   100%
src\weather\service.py            21      0   100%
--------------------------------------------------
TOTAL                             57      0   100%
```

## Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

Hooks: **black** (formatting) · **ruff** (linting + import order) · **mypy** (strict type checking)

---

## Known Cities (Mock Data)

| City | Temp (°C) | Condition | Humidity |
|---|---|---|---|
| Accra | 32.0 | Sunny | 60% |
| Berlin | 14.0 | Cloudy | 72% |
| Tokyo | 22.0 | Partly Cloudy | 65% |
| New York | 18.0 | Windy | 55% |
| Lagos | 30.0 | Humid | 85% |
