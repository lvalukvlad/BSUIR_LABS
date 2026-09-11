"""Secure Notes Lab — учебное приложение для лаб. №2 ПЗИИС (часть 1)."""
from __future__ import annotations

import os
import secrets
from datetime import datetime
from functools import wraps

from cryptography.fernet import Fernet, InvalidToken
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "secure_notes.db")
KEY_PATH = os.path.join(BASE_DIR, "instance", "fernet.key")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("LAB2_SECRET_KEY", secrets.token_hex(32))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# Для локальной демонстрации HTTPS обычно нет:
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("LAB2_HTTPS", "") == "1"

db = SQLAlchemy(app)


def _ensure_instance() -> None:
    os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)
    if not os.path.exists(KEY_PATH):
        with open(KEY_PATH, "wb") as f:
            f.write(Fernet.generate_key())


def get_fernet() -> Fernet:
    _ensure_instance()
    with open(KEY_PATH, "rb") as f:
        return Fernet(f.read())


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    notes = db.relationship("Note", backref="owner", lazy=True, cascade="all, delete")
    secrets = db.relationship("Secret", backref="owner", lazy=True, cascade="all, delete")


class Note(db.Model):
    """Неконфиденциальные данные (заметки)."""

    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Secret(db.Model):
    """Конфиденциальные данные (шифруются на диске)."""

    __tablename__ = "secrets"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    body_encrypted = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_body(self, plain: str) -> None:
        self.body_encrypted = get_fernet().encrypt(plain.encode("utf-8"))

    def get_body(self) -> str:
        try:
            return get_fernet().decrypt(self.body_encrypted).decode("utf-8")
        except InvalidToken:
            return "[ошибка расшифрования]"


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Требуется авторизация.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def current_user() -> User | None:
    uid = session.get("user_id")
    if not uid:
        return None
    return db.session.get(User, uid)


@app.before_request
def _ensure_csrf():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(16)


@app.before_request
def _csrf_protect():
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        # Исключения не нужны: формы всегда несут _csrf
        token = session.get("_csrf")
        sent = request.form.get("_csrf") or request.headers.get("X-CSRF-Token")
        if not token or not sent or not secrets.compare_digest(str(token), str(sent)):
            abort(400, description="CSRF token missing or invalid")


@app.context_processor
def inject_globals():
    return {"current_user": current_user(), "csrf_token": session.get("_csrf", "")}


@app.route("/")
def index():
    if current_user():
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user():
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if len(username) < 3 or len(username) > 64:
            flash("Имя пользователя: 3–64 символа.", "error")
        elif len(password) < 8:
            flash("Пароль не короче 8 символов.", "error")
        elif User.query.filter_by(username=username).first():
            flash("Такой пользователь уже существует.", "error")
        else:
            user = User(
                username=username,
                password_hash=generate_password_hash(password, method="pbkdf2:sha256"),
            )
            db.session.add(user)
            db.session.commit()
            flash("Пользователь создан. Войдите.", "ok")
            return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session["user_id"] = user.id
            session["_csrf"] = secrets.token_hex(16)
            flash(f"Добро пожаловать, {user.username}.", "ok")
            return redirect(url_for("dashboard"))
        flash("Неверные идентификационные данные.", "error")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("Вы вышли из системы.", "ok")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    return render_template(
        "dashboard.html",
        notes_count=Note.query.filter_by(user_id=user.id).count(),
        secrets_count=Secret.query.filter_by(user_id=user.id).count(),
    )


# ---- Неконфиденциальные заметки ----


@app.route("/notes")
@login_required
def notes_list():
    user = current_user()
    q = (request.args.get("q") or "").strip()
    query = Note.query.filter_by(user_id=user.id)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Note.title.ilike(like), Note.body.ilike(like)))
    notes = query.order_by(Note.updated_at.desc()).all()
    return render_template("notes_list.html", notes=notes, q=q)


@app.route("/notes/new", methods=["GET", "POST"])
@login_required
def notes_create():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        body = request.form.get("body") or ""
        if not title:
            flash("Заголовок обязателен.", "error")
        else:
            note = Note(user_id=current_user().id, title=title[:200], body=body)
            db.session.add(note)
            db.session.commit()
            flash("Заметка создана.", "ok")
            return redirect(url_for("notes_list"))
    return render_template("note_form.html", note=None)


@app.route("/notes/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def notes_edit(note_id: int):
    note = Note.query.filter_by(id=note_id, user_id=current_user().id).first_or_404()
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        body = request.form.get("body") or ""
        if not title:
            flash("Заголовок обязателен.", "error")
        else:
            note.title = title[:200]
            note.body = body
            note.updated_at = datetime.utcnow()
            db.session.commit()
            flash("Заметка обновлена.", "ok")
            return redirect(url_for("notes_list"))
    return render_template("note_form.html", note=note)


@app.route("/notes/<int:note_id>/delete", methods=["POST"])
@login_required
def notes_delete(note_id: int):
    note = Note.query.filter_by(id=note_id, user_id=current_user().id).first_or_404()
    db.session.delete(note)
    db.session.commit()
    flash("Заметка удалена.", "ok")
    return redirect(url_for("notes_list"))


# ---- Конфиденциальные секреты ----


@app.route("/secrets")
@login_required
def secrets_list():
    user = current_user()
    q = (request.args.get("q") or "").strip()
    secrets_q = Secret.query.filter_by(user_id=user.id).order_by(Secret.updated_at.desc()).all()
    # Поиск по заголовку и расшифрованному телу только у владельца
    if q:
        ql = q.lower()
        secrets_q = [
            s
            for s in secrets_q
            if ql in s.title.lower() or ql in s.get_body().lower()
        ]
    return render_template("secrets_list.html", secrets=secrets_q, q=q)


@app.route("/secrets/new", methods=["GET", "POST"])
@login_required
def secrets_create():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        body = request.form.get("body") or ""
        if not title:
            flash("Заголовок обязателен.", "error")
        else:
            secret = Secret(user_id=current_user().id, title=title[:200])
            secret.set_body(body)
            db.session.add(secret)
            db.session.commit()
            flash("Конфиденциальная запись создана (данные зашифрованы).", "ok")
            return redirect(url_for("secrets_list"))
    return render_template("secret_form.html", secret=None, body="")


@app.route("/secrets/<int:secret_id>/edit", methods=["GET", "POST"])
@login_required
def secrets_edit(secret_id: int):
    secret = Secret.query.filter_by(id=secret_id, user_id=current_user().id).first_or_404()
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        body = request.form.get("body") or ""
        if not title:
            flash("Заголовок обязателен.", "error")
        else:
            secret.title = title[:200]
            secret.set_body(body)
            secret.updated_at = datetime.utcnow()
            db.session.commit()
            flash("Конфиденциальная запись обновлена.", "ok")
            return redirect(url_for("secrets_list"))
    return render_template("secret_form.html", secret=secret, body=secret.get_body())


@app.route("/secrets/<int:secret_id>/delete", methods=["POST"])
@login_required
def secrets_delete(secret_id: int):
    secret = Secret.query.filter_by(id=secret_id, user_id=current_user().id).first_or_404()
    db.session.delete(secret)
    db.session.commit()
    flash("Конфиденциальная запись удалена.", "ok")
    return redirect(url_for("secrets_list"))


def init_db() -> None:
    _ensure_instance()
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    init_db()
    # 127.0.0.1 — не слушаем все интерфейсы без явного согласия
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5050")), debug=False)
