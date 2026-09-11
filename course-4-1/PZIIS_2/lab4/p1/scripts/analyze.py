#!/usr/bin/env python3
"""Разбор Combined и auth.log: сводка по дням, адресам и классам запросов."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
OUT = LOG_DIR / "analysis.json"

COMBINED = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<ts>[^\]]+)\] "(?P<method>\S+) (?P<uri>\S+) (?P<proto>[^"]+)" '
    r'(?P<status>\d+) (?P<size>\d+) "(?P<ref>[^"]*)" "(?P<ua>[^"]*)"'
)

SSH = re.compile(
    r'^(?P<mon>\w{3})\s+(?P<day>\d+)\s+(?P<time>\d{2}:\d{2}:\d{2})\s+\S+\s+sshd\[\d+\]:\s+(?P<msg>.*)$'
)


def http_class(uri: str, ua: str) -> str:
    u = uri.lower()
    ua_l = ua.lower()
    if ".." in u or "etc/passwd" in u:
        return "обход пути"
    if any(x in u for x in ("union", "or+", "'1'='1", "select+")):
        return "инъекция в URI"
    if any(x in u for x in (".env", ".git", "wp-config")):
        return "утечка секретов"
    if any(x in u for x in ("wp-", "xmlrpc", "phpmyadmin", "/admin")):
        return "сканер CMS"
    if any(x in ua_l for x in ("sqlmap", "hydra", "nmap", "masscan", "zgrab")):
        return "сканер по UA"
    if u in ("/", "/status.json", "/robots.txt", "/health"):
        return "легитимный"
    return "прочее"


def parse_http(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = COMBINED.match(line)
        if not m:
            continue
        d = m.groupdict()
        d["status"] = int(d["status"])
        d["size"] = int(d["size"])
        d["klass"] = http_class(d["uri"], d["ua"])
        d["day"] = d["ts"][:11]
        rows.append(d)
    return rows


def parse_ssh(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = SSH.match(line)
        if not m:
            continue
        msg = m.group("msg")
        kind = "прочее"
        user = ""
        ip = ""
        if msg.startswith("Accepted"):
            kind = "успех"
        elif "invalid user" in msg.lower() or msg.startswith("Invalid user"):
            kind = "несуществующий пользователь"
        elif msg.startswith("Failed password"):
            kind = "неверный пароль"
        elif "Too many authentication failures" in msg:
            kind = "отключение после перебора"
        elif "Did not receive identification" in msg:
            kind = "нет баннера"
        um = re.search(r"user (\S+)", msg)
        if um:
            user = um.group(1)
        im = re.search(r"from (\d+\.\d+\.\d+\.\d+)", msg) or re.search(
            r"from (\d+\.\d+\.\d+\.\d+)", msg
        )
        if not im:
            im = re.search(r"(\d+\.\d+\.\d+\.\d+)", msg)
        if im:
            ip = im.group(1)
        rows.append(
            {
                "day": f"{m.group('mon')} {m.group('day').rjust(2)}",
                "kind": kind,
                "user": user,
                "ip": ip,
                "msg": msg,
            }
        )
    return rows


def top(counter: Counter, n: int = 8) -> list[list]:
    return [[k, v] for k, v in counter.most_common(n)]


def main() -> None:
    http = parse_http(LOG_DIR / "access.log")
    ssh = parse_ssh(LOG_DIR / "auth.log")
    http_by_day = Counter(r["day"] for r in http)
    ssh_by_day = Counter(r["day"] for r in ssh)
    summary = {
        "http_total": len(http),
        "ssh_total": len(ssh),
        "http_status": dict(Counter(r["status"] for r in http)),
        "http_class": dict(Counter(r["klass"] for r in http)),
        "http_top_ip": top(Counter(r["ip"] for r in http)),
        "http_by_day": dict(http_by_day),
        "ssh_kind": dict(Counter(r["kind"] for r in ssh)),
        "ssh_top_ip": top(Counter(r["ip"] for r in ssh if r["ip"])),
        "ssh_by_day": dict(ssh_by_day),
        "ssh_users": dict(Counter(r["user"] for r in ssh if r["user"])),
        "correlated": sorted(
            set(r["ip"] for r in http if r["klass"] != "легитимный")
            & set(r["ip"] for r in ssh if r["kind"] != "успех")
        ),
    }
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
