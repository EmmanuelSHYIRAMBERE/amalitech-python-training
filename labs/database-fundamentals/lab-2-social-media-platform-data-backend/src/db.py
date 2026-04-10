"""PostgreSQL connection pool (psycopg2 ThreadedConnectionPool)."""

import os
from collections.abc import Generator
from contextlib import contextmanager

from psycopg2 import pool
from psycopg2.extensions import connection as PgConnection

_DSN = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:social_pass@127.0.0.1:5434/social",
)

_pool: pool.ThreadedConnectionPool | None = None


def get_pool() -> pool.ThreadedConnectionPool:
    global _pool
    if _pool is None:
        _pool = pool.ThreadedConnectionPool(minconn=1, maxconn=10, dsn=_DSN)
    return _pool


@contextmanager
def get_conn() -> Generator[PgConnection, None, None]:
    """Yield a connection from the pool and return it afterwards."""
    conn = get_pool().getconn()
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        get_pool().putconn(conn)
