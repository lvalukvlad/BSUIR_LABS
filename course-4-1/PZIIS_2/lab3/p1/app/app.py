"""Приложение с CRUD данных в оперативной памяти и шифрованием секретов."""
from __future__ import annotations

import gc
import os
import secrets
import threading
import time
from dataclasses import dataclass, field

from cryptography.fernet import Fernet, InvalidToken
from flask import Flask, flash, redirect, render_template, request, url_for

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
KEY_PATH = os.path.join(BASE_DIR, "instance", "fernet.key")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("LAB3_SECRET_KEY", secrets.token_hex(32))
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

_lock = threading.Lock()
_notes: dict[int, "Note"] = {}
_secrets: dict[int, "Secret"] = {}
_next_note_id = 1
_next_secret_id = 1
_started_at = time.time()
_fernet: Fernet | None = None


def _ensure_key() -> bytes:
    os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)
    if not os.path.exists(KEY_PATH):
        with open(KEY_PATH, "wb") as f:
            f.write(Fernet.generate_key())
        os.chmod(KEY_PATH, 0o600)
    with open(KEY_PATH, "rb") as f:
        return f.read()


def get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        _fernet = Fernet(_ensure_key())
    return _fernet


def wipe_bytes(buf: bytearray) -> None:
    for i in range(len(buf)):
        buf[i] = 0
    buf.clear()


@dataclass
class Note:
    id: int
    title: str
    body: str
    updated_at: float = field(default_factory=time.time)


@dataclass
class Secret:
    id: int
    title: str
    ciphertext: bytes
    updated_at: float = field(default_factory=time.time)


@app.context_processor
def inject_meta():
    return {
        "notes_count": len(_notes),
        "secrets_count": len(_secrets),
    }


@app.get("/")
def index():
    with _lock:
        notes = sorted(_notes.values(), key=lambda n: n.id)
        secrets = sorted(_secrets.values(), key=lambda s: s.id)
    return render_template("index.html", notes=notes, secrets=secrets)


@app.post("/notes")
def note_create():
    global _next_note_id
    title = (request.form.get("title") or "").strip()
    body = (request.form.get("body") or "").strip()
    if not title:
        flash("Укажите заголовок заметки.", "error")
        return redirect(url_for("index"))
    if len(title) > 200 or len(body) > 10000:
        flash("Превышена допустимая длина заметки.", "error")
        return redirect(url_for("index"))
    with _lock:
        nid = _next_note_id
        _next_note_id += 1
        _notes[nid] = Note(id=nid, title=title, body=body)
    flash("Заметка сохранена.", "ok")
    return redirect(url_for("index"))


@app.post("/notes/<int:nid>/update")
def note_update(nid: int):
    title = (request.form.get("title") or "").strip()
    body = (request.form.get("body") or "").strip()
    with _lock:
        note = _notes.get(nid)
        if not note:
            flash("Заметка не найдена.", "error")
            return redirect(url_for("index"))
        if title:
            note.title = title
        note.body = body
        note.updated_at = time.time()
    flash("Заметка обновлена.", "ok")
    return redirect(url_for("index"))


@app.post("/notes/<int:nid>/delete")
def note_delete(nid: int):
    with _lock:
        if nid in _notes:
            del _notes[nid]
            flash("Заметка удалена.", "ok")
        else:
            flash("Заметка не найдена.", "error")
    return redirect(url_for("index"))


def _encrypt_plain(plain: str) -> bytes:
    buf = bytearray(plain.encode("utf-8"))
    try:
        return get_fernet().encrypt(bytes(buf))
    finally:
        wipe_bytes(buf)
        gc.collect()


@app.post("/secrets")
def secret_create():
    global _next_secret_id
    title = (request.form.get("title") or "").strip()
    plain = request.form.get("body") or ""
    if not title or not plain:
        flash("Укажите заголовок и текст секрета.", "error")
        return redirect(url_for("index"))
    if len(title) > 200 or len(plain) > 10000:
        flash("Превышена допустимая длина секрета.", "error")
        return redirect(url_for("index"))

    token = _encrypt_plain(plain)
    plain = ""
    with _lock:
        sid = _next_secret_id
        _next_secret_id += 1
        _secrets[sid] = Secret(id=sid, title=title, ciphertext=token)
    flash("Секрет сохранён.", "ok")
    return redirect(url_for("index"))


@app.post("/secrets/<int:sid>/update")
def secret_update(sid: int):
    title = (request.form.get("title") or "").strip()
    plain = request.form.get("body") or ""
    with _lock:
        sec = _secrets.get(sid)
        if not sec:
            flash("Секрет не найден.", "error")
            return redirect(url_for("index"))
        if title:
            sec.title = title
        if plain:
            sec.ciphertext = _encrypt_plain(plain)
            plain = ""
        sec.updated_at = time.time()
    flash("Секрет обновлён.", "ok")
    return redirect(url_for("index"))


@app.post("/secrets/<int:sid>/delete")
def secret_delete(sid: int):
    with _lock:
        sec = _secrets.pop(sid, None)
        if sec is None:
            flash("Секрет не найден.", "error")
        else:
            sec.ciphertext = b""
            flash("Секрет удалён.", "ok")
    return redirect(url_for("index"))


@app.get("/secrets/<int:sid>/reveal")
def secret_reveal(sid: int):
    with _lock:
        sec = _secrets.get(sid)
        if not sec:
            flash("Секрет не найден.", "error")
            return redirect(url_for("index"))
        try:
            text = get_fernet().decrypt(sec.ciphertext).decode("utf-8")
        except InvalidToken:
            flash("Не удалось расшифровать секрет.", "error")
            return redirect(url_for("index"))
        title = sec.title
    return render_template("reveal.html", title=title, body=text)


@app.get("/health")
def health():
    return {
        "ok": True,
        "pid": os.getpid(),
        "notes": len(_notes),
        "secrets": len(_secrets),
        "uptime_s": int(time.time() - _started_at),
    }


def _allow_ptrace_for_dumps() -> None:
    try:
        import ctypes

        PR_SET_PTRACER = 0x59616D61
        PR_SET_PTRACER_ANY = -1
        ctypes.CDLL(None, use_errno=True).prctl(
            PR_SET_PTRACER, PR_SET_PTRACER_ANY, 0, 0, 0
        )
    except Exception:
        pass


if __name__ == "__main__":
    _ensure_key()
    _allow_ptrace_for_dumps()
    host = os.environ.get("LAB3_HOST", "127.0.0.1")
    port = int(os.environ.get("LAB3_PORT", "5070"))
    print(f"http://127.0.0.1:{port}/")
    app.run(host=host, port=port, debug=False)
