#!/usr/bin/env python3
"""Создать двух пользователей и записи для демонстрации защищённости."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

from app import Note, Secret, User, app, db, init_db  # noqa: E402
from werkzeug.security import generate_password_hash


def main() -> None:
    init_db()
    with app.app_context():
        db.drop_all()
        db.create_all()
        alice = User(
            username="alice",
            password_hash=generate_password_hash("alice-pass-1", method="pbkdf2:sha256"),
        )
        bob = User(
            username="bob",
            password_hash=generate_password_hash("bob-pass-22", method="pbkdf2:sha256"),
        )
        db.session.add_all([alice, bob])
        db.session.commit()
        note = Note(user_id=alice.id, title="Повестка", body="встреча в 10:00")
        secret = Secret(user_id=alice.id, title="PIN")
        secret.set_body("1234-secret")
        db.session.add_all([note, secret])
        db.session.commit()
        print(f"alice_id={alice.id} bob_id={bob.id} secret_id={secret.id} note_id={note.id}")


if __name__ == "__main__":
    main()
