#!/usr/bin/env python3
"""Учебный узел: публичная страница и журнал Combined."""

from __future__ import annotations

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

HOST = os.environ.get("LAB4_HTTP_HOST", "0.0.0.0")
PORT = int(os.environ.get("LAB4_HTTP_PORT", "8088"))
MINSK = timezone(timedelta(hours=3))

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
    )


@app.get("/status.json")
def status_json():
    body = {
        "state": "up",
        "http": "ok",
        "ssh": "key-only",
        "generated": _now().isoformat(),
    }
    return body


@app.get("/robots.txt")
def robots():
    body = "User-agent: *\nDisallow: /status.json\n"
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
