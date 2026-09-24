import time
from contextlib import contextmanager

import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool

from .config import DB_CONFIG

pool = None


def init_pool(tries=30, wait=2.0):
    global pool
    if pool is not None:
        return
    err = None
    for _ in range(tries):
        try:
            pool = ThreadedConnectionPool(minconn=1, maxconn=8, **DB_CONFIG)
            return
        except psycopg2.OperationalError as e:
            err = e
            time.sleep(wait)
    raise RuntimeError(f"нет соединения с бд: {err}")


def close_pool():
    global pool
    if pool is not None:
        pool.closeall()
        pool = None


@contextmanager
def get_connection():
    if pool is None:
        init_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


@contextmanager
def get_cursor(as_dict=True):
    with get_connection() as conn:
        factory = psycopg2.extras.RealDictCursor if as_dict else None
        cur = conn.cursor(cursor_factory=factory)
        try:
            yield cur
        finally:
            cur.close()


def fetch_all(sql, params=None):
    with get_cursor() as cur:
        cur.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]


def fetch_one(sql, params=None):
    with get_cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None


def execute(sql, params=None):
    with get_cursor() as cur:
        cur.execute(sql, params)
