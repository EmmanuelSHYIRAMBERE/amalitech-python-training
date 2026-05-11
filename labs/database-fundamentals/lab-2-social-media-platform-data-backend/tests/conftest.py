"""Shared pytest fixtures — all external I/O is mocked."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from unittest.mock import MagicMock

import pytest


def make_cursor(fetchone_val: Any = None, fetchall_val: list[Any] | None = None) -> MagicMock:
    cur = MagicMock()
    cur.fetchone.return_value = fetchone_val
    cur.fetchall.return_value = fetchall_val or []
    cur.__enter__ = lambda s: s
    cur.__exit__ = MagicMock(return_value=False)
    return cur


def make_conn(cursor: MagicMock) -> MagicMock:
    conn = MagicMock()
    conn.cursor.return_value = cursor
    conn.__enter__ = lambda s: s
    conn.__exit__ = MagicMock(return_value=False)
    return conn


@contextmanager
def fake_get_conn(conn: MagicMock) -> Generator[MagicMock, None, None]:
    yield conn


@pytest.fixture
def mock_cursor() -> MagicMock:
    return make_cursor()


@pytest.fixture
def mock_conn(mock_cursor: MagicMock) -> MagicMock:
    return make_conn(mock_cursor)


@pytest.fixture
def mock_redis() -> MagicMock:
    r = MagicMock()
    r.get.return_value = None
    return r


@pytest.fixture
def mock_collection() -> MagicMock:
    col = MagicMock()
    col.find_one.return_value = None
    return col
