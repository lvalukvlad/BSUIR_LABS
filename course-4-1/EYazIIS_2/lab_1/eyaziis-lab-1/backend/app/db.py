"""Доступ к PostgreSQL: пул соединений и вспомогательные обёртки."""
import time
from contextlib import contextmanager

import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool

from .config import DB_CONFIG

_pool: ThreadedConnectionPool | None = None


def init_pool(retries: int = 30, delay: float = 2.0) -> None:
    """Создаёт пул соединений, дожидаясь готовности СУБД."""
    global _pool
    if _pool is not None:
        return
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            _pool = ThreadedConnectionPool(minconn=1, maxconn=10, **DB_CONFIG)
            return
        except psycopg2.OperationalError as exc:
            last_error = exc
            time.sleep(delay)
    raise RuntimeError(f"Не удалось подключиться к базе данных: {last_error}")


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None


@contextmanager
def get_connection():
    if _pool is None:
        init_pool()
    conn = _pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)


@contextmanager
def get_cursor(dict_rows: bool = True):
    with get_connection() as conn:
        factory = psycopg2.extras.RealDictCursor if dict_rows else None
        cur = conn.cursor(cursor_factory=factory)
        try:
            yield cur
        finally:
            cur.close()


def fetch_all(sql: str, params: tuple | dict | None = None) -> list[dict]:
    with get_cursor() as cur:
        cur.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]


def fetch_one(sql: str, params: tuple | dict | None = None) -> dict | None:
    with get_cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None


def execute(sql: str, params: tuple | dict | None = None) -> None:
    with get_cursor() as cur:
        cur.execute(sql, params)
