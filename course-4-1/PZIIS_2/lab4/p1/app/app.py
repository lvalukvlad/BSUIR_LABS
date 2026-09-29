#!/usr/bin/env python3

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

from flask import Flask, Response, abort, render_template, request

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = Path(os.environ.get("LAB4_LOG_DIR", ROOT / "logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
ACCESS_LOG = LOG_DIR / "access.log"
ERROR_LOG = LOG_DIR / "error.log"
AUTH_LOG = LOG_DIR / "auth.log"
ANALYSIS_JSON = LOG_DIR / "analysis.json"

IDS_LOG_DIR = Path(os.environ.get("LAB4_IDS_LOG_DIR", ROOT.parent / "p2" / "logs"))
ALERT_LOG = IDS_LOG_DIR / "alert"
BLOCKLIST = IDS_LOG_DIR / "blocklist.txt"
IDS_ANALYSIS_JSON = IDS_LOG_DIR / "ids_analysis.json"

HOST = os.environ.get("LAB4_HTTP_HOST", "0.0.0.0")
PORT = int(os.environ.get("LAB4_HTTP_PORT", "8088"))
MINSK = timezone(timedelta(hours=3))

# Имя → путь. Только эти журналы доступны через веб.
LOG_FILES: dict[str, Path] = {
    "access": ACCESS_LOG,
    "auth": AUTH_LOG,
    "error": ERROR_LOG,
    "alert": ALERT_LOG,
    "blocklist": BLOCKLIST,
}

LOG_TITLES = {
    "access": "access.log — Combined HTTP",
    "auth": "auth.log — SSH",
    "error": "error.log — отказы 4xx",
    "alert": "alert — срабатывания Snort",
    "blocklist": "blocklist — адреса для ACL",
}

app = Flask(__name__)
logging.getLogger("werkzeug").setLevel(logging.ERROR)


def _now() -> datetime:
    return datetime.now(MINSK)


def _stamp() -> str:
    return _now().strftime("%d/%b/%Y:%H:%M:%S %z")


def _uri() -> str:
    uri = request.full_path
    if uri.endswith("?"):
        uri = uri[:-1]
    return uri


def _client() -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "-"


def write_access(status: int, length: int) -> None:
    line = (
        f'{_client()} - - [{_stamp()}] '
        f'"{request.method} {_uri()} {request.environ.get("SERVER_PROTOCOL", "HTTP/1.1")}" '
        f'{status} {length} '
        f'"{request.headers.get("Referer", "-")}" '
        f'"{request.headers.get("User-Agent", "-")}"\n'
    )
    with ACCESS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(line)


def write_error(status: int, length: int) -> None:
    if status < 400:
        return
    line = (
        f'[{_now().strftime("%a %b %d %H:%M:%S.%f %Y")}] '
        f'[client {_client()}] {status} for {_uri()} '
        f'ua="{request.headers.get("User-Agent", "-")}"\n'
    )
    with ERROR_LOG.open("a", encoding="utf-8") as fh:
        fh.write(line)


def _read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _tail(path: Path, limit: int | None = 40) -> tuple[list[str], int]:
    if not path.is_file():
        return [], 0
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [], 0
    lines = [ln for ln in text.splitlines() if ln.strip() != ""]
    total = len(lines)
    if limit is None or limit <= 0 or limit >= total:
        return lines, total
    return lines[-limit:], total


def _parse_limit(raw: str | None, default: int = 80) -> int | None:
    """None = весь файл. Иначе число строк с конца."""
    if raw is None or raw == "":
        return default
    key = raw.strip().lower()
    if key in ("all", "все", "0", "-1"):
        return None
    try:
        n = int(key)
    except ValueError:
        return default
    if n <= 0:
        return None
    return min(n, 5000)


def _summary() -> dict:
    analysis = _read_json(ANALYSIS_JSON) or {}
    ids = _read_json(IDS_ANALYSIS_JSON) or {}
    access_lines, access_n = _tail(ACCESS_LOG, 1)
    auth_lines, auth_n = _tail(AUTH_LOG, 1)
    _, alert_n = _tail(ALERT_LOG, 1)
    return {
        "http_total": analysis.get("http_total", access_n),
        "ssh_total": analysis.get("ssh_total", auth_n),
        "alerts": ids.get("alerts", alert_n),
        "blocklist": ids.get("blocklist")
        or ([ln.strip() for ln in _tail(BLOCKLIST, 50)[0] if ln.strip()]),
        "http_class": analysis.get("http_class") or {},
        "ssh_kind": analysis.get("ssh_kind") or {},
    }


@app.after_request
def combined_log(response: Response) -> Response:
    length = response.content_length
    if length is None:
        try:
            length = len(response.get_data())
        except RuntimeError:
            length = 0
    write_access(response.status_code, length)
    write_error(response.status_code, length)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Server"] = "node-http"
    return response


@app.get("/")
def index():
    return render_template(
        "index.html",
        generated=_now().strftime("%d.%m.%Y %H:%M %z"),
        http_port=PORT,
        summary=_summary(),
    )


@app.get("/logs/")
@app.get("/logs")
def logs_index():
    items = []
    for key, path in LOG_FILES.items():
        _, total = _tail(path, 1)
        items.append(
            {
                "key": key,
                "title": LOG_TITLES[key],
                "exists": path.is_file(),
                "lines": total,
            }
        )
    return render_template(
        "logs.html",
        generated=_now().strftime("%d.%m.%Y %H:%M %z"),
        items=items,
        summary=_summary(),
    )


@app.get("/logs/<name>")
def logs_view(name: str):
    path = LOG_FILES.get(name)
    if path is None:
        abort(404)
    limit = _parse_limit(request.args.get("n"), default=80)
    lines, total = _tail(path, limit)
    return render_template(
        "log_view.html",
        generated=_now().strftime("%d.%m.%Y %H:%M %z"),
        name=name,
        title=LOG_TITLES[name],
        lines=lines,
        total=total,
        shown=len(lines),
        limit=limit,
        show_all=(limit is None or len(lines) >= total),
    )


@app.get("/status.json")
def status_json():
    s = _summary()
    body = {
        "state": "up",
        "http": "ok",
        "ssh": "key-only",
        "generated": _now().isoformat(),
        "http_total": s["http_total"],
        "ssh_total": s["ssh_total"],
        "alerts": s["alerts"],
    }
    return body


@app.get("/robots.txt")
def robots():
    body = "User-agent: *\nDisallow: /status.json\nAllow: /logs\n"
    return Response(body, mimetype="text/plain")


@app.get("/health")
def health():
    return Response("ok\n", mimetype="text/plain")


@app.errorhandler(404)
def not_found(_err):
    return render_template("missing.html"), 404


@app.errorhandler(400)
def bad_request(_err):
    return render_template("missing.html"), 400


@app.before_request
def reject_traversal():
    uri = _uri()
    if ".." in uri or "\\x" in uri.lower():
        abort(400)


def main() -> None:
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
