#!/usr/bin/env python3
"""Проверка защищённости на диске: права файлов и вид записей в SQLite."""

from __future__ import annotations

import os
import sqlite3
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTANCE = ROOT / "instance"
DB = INSTANCE / "notes.db"
KEY = INSTANCE / "fernet.key"
SECRET = INSTANCE / "flask.secret"


def mode(path: Path) -> str:
    return oct(path.stat().st_mode & 0o777)


def main() -> None:
    print("=== права ===")
    for p in (INSTANCE, KEY, SECRET, DB):
        if p.exists():
            print(f"{p.name}: {mode(p)}")
        else:
            print(f"{p.name}: нет файла")

    if not DB.exists():
        return
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    print("\n=== notes (открытый текст) ===")
    for row in con.execute("SELECT id, title, substr(body,1,60) AS body FROM notes"):
        print(dict(row))
    print("\n=== secrets (тело — BLOB/шифртекст) ===")
    for row in con.execute(
        "SELECT id, title, length(body_encrypted) AS n, substr(hex(body_encrypted),1,24) AS hex FROM secrets"
    ):
        print(dict(row))
    print("\n=== users (пароль — хэш) ===")
    for row in con.execute("SELECT id, username, substr(password_hash,1,28) AS hash FROM users"):
        print(dict(row))
    con.close()


if __name__ == "__main__":
    os.chdir(ROOT)
    main()
