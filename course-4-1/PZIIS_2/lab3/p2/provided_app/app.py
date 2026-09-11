"""Provided insecure reference — лаб. №3 ПЗИИС, часть 2 (для сравнения).

Хранит конфиденциальные данные открытым текстом (str) в ОЗУ без шифрования
и без затирания буферов.
"""
from __future__ import annotations

import os
import secrets
import threading
import time
from dataclasses import dataclass, field

from flask import Flask, flash, redirect, render_template_string, request, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(16)

_lock = threading.Lock()
_notes: dict[int, "Note"] = {}
_secrets: dict[int, "Secret"] = {}
_next_note_id = 1
_next_secret_id = 1

PAGE = """
<!doctype html><html lang="ru"><head><meta charset="utf-8">
<title>Provided Insecure Vault</title>
<style>
body{font-family:sans-serif;max-width:900px;margin:1.5rem auto;padding:0 1rem}
.item{border:1px solid #ccc;padding:.75rem;margin:.5rem 0}
.warn{color:#a00;font-weight:700}
</style></head><body>
<h1>Provided Insecure Vault</h1>
<p class="warn">Учебный «предоставленный» вариант: секреты в ОЗУ как plaintext str.</p>
<p>PID {{ pid }}</p>
{% with messages = get_flashed_messages() %}{% if messages %}<ul>{% for m in messages %}<li>{{ m }}</li>{% endfor %}</ul>{% endif %}{% endwith %}
<h2>Notes</h2>
<form method="post" action="{{ url_for('note_create') }}">
<input name="title" placeholder="title" required>
<textarea name="body"></textarea>
<button>create note</button>
</form>
{% for n in notes %}<div class="item">#{{ n.id }} {{ n.title }}<pre>{{ n.body }}</pre>
<form method="post" action="{{ url_for('note_update', nid=n.id) }}">
<input name="title" value="{{ n.title }}"><textarea name="body">{{ n.body }}</textarea>
<button>update</button></form>
<form method="post" action="{{ url_for('note_delete', nid=n.id) }}"><button>delete</button></form>
</div>{% endfor %}
<h2>Secrets (PLAINTEXT IN RAM)</h2>
<form method="post" action="{{ url_for('secret_create') }}">
<input name="title" placeholder="title" required>
<textarea name="body" required></textarea>
<button>create secret</button>
</form>
{% for s in secrets %}<div class="item">#{{ s.id }} {{ s.title }}
<pre class="warn">{{ s.body }}</pre>
<form method="post" action="{{ url_for('secret_update', sid=s.id) }}">
<input name="title" value="{{ s.title }}"><textarea name="body">{{ s.body }}</textarea>
<button>update</button></form>
<form method="post" action="{{ url_for('secret_delete', sid=s.id) }}"><button>delete</button></form>
</div>{% endfor %}
</body></html>
"""


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
    body: str  # plaintext intentionally
    updated_at: float = field(default_factory=time.time)


@app.get("/")
def index():
    with _lock:
        notes = sorted(_notes.values(), key=lambda n: n.id)
        secrets = sorted(_secrets.values(), key=lambda s: s.id)
    return render_template_string(PAGE, notes=notes, secrets=secrets, pid=os.getpid())


@app.post("/notes")
def note_create():
    global _next_note_id
    title = (request.form.get("title") or "").strip()
    body = request.form.get("body") or ""
    with _lock:
        nid = _next_note_id
        _next_note_id += 1
        _notes[nid] = Note(id=nid, title=title, body=body)
    flash(f"note {nid} created")
    return redirect(url_for("index"))


@app.post("/notes/<int:nid>/update")
def note_update(nid: int):
    with _lock:
        n = _notes.get(nid)
        if n:
            n.title = (request.form.get("title") or n.title).strip() or n.title
            n.body = request.form.get("body") or ""
            n.updated_at = time.time()
    return redirect(url_for("index"))


@app.post("/notes/<int:nid>/delete")
def note_delete(nid: int):
    with _lock:
        _notes.pop(nid, None)
    return redirect(url_for("index"))


@app.post("/secrets")
def secret_create():
    global _next_secret_id
    title = (request.form.get("title") or "").strip()
    body = request.form.get("body") or ""
    with _lock:
        sid = _next_secret_id
        _next_secret_id += 1
        _secrets[sid] = Secret(id=sid, title=title, body=body)
    flash(f"secret {sid} stored as plaintext")
    return redirect(url_for("index"))


@app.post("/secrets/<int:sid>/update")
def secret_update(sid: int):
    with _lock:
        s = _secrets.get(sid)
        if s:
            s.title = (request.form.get("title") or s.title).strip() or s.title
            if request.form.get("body") is not None:
                s.body = request.form.get("body") or ""
            s.updated_at = time.time()
    return redirect(url_for("index"))


@app.post("/secrets/<int:sid>/delete")
def secret_delete(sid: int):
    with _lock:
        _secrets.pop(sid, None)
    return redirect(url_for("index"))


@app.get("/health")
def health():
    return {"ok": True, "pid": os.getpid(), "mode": "insecure_plaintext"}


if __name__ == "__main__":
    try:
        import ctypes

        PR_SET_PTRACER = 0x59616D61
        PR_SET_PTRACER_ANY = -1
        ctypes.CDLL(None, use_errno=True).prctl(
            PR_SET_PTRACER, PR_SET_PTRACER_ANY, 0, 0, 0
        )
    except Exception:
        pass
    app.run(host="127.0.0.1", port=int(os.environ.get("LAB3_PROVIDED_PORT", "5071")), debug=False)
