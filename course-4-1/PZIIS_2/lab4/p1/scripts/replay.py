#!/usr/bin/env python3
"""Живые запросы к HTTP и SSH — дописывают текущие строки в журналы."""

from __future__ import annotations

import os
import urllib.error
import urllib.request
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
HTTP = os.environ.get("LAB4_HTTP_URL", "http://127.0.0.1:8088")
SSH_HOST = os.environ.get("LAB4_SSH_HOST", "127.0.0.1")
SSH_PORT = int(os.environ.get("LAB4_SSH_PORT", "2222"))
KEY = ROOT / "keys" / "operator"


def hit(path: str, ua: str = "lab4-replay/1.0") -> None:
    req = urllib.request.Request(HTTP + path, headers={"User-Agent": ua})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            resp.read()
            print(f"{resp.status} {path}")
    except urllib.error.HTTPError as exc:
        print(f"{exc.code} {path}")
    except Exception as exc:  # noqa: BLE001
        print(f"ERR {path} {exc}")


def ssh_try(username: str, password: str | None = None, keyfile: Path | None = None) -> None:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        kwargs = {
            "hostname": SSH_HOST,
            "port": SSH_PORT,
            "username": username,
            "timeout": 8,
            "allow_agent": False,
            "look_for_keys": False,
        }
        if keyfile:
            kwargs["pkey"] = paramiko.RSAKey.from_private_key_file(str(keyfile))
        else:
            kwargs["password"] = password or "wrong"
        client.connect(**kwargs)
        print(f"ssh ok {username}")
    except Exception as exc:  # noqa: BLE001
        print(f"ssh fail {username}: {type(exc).__name__}")
    finally:
        client.close()


def main() -> None:
    hit("/", "Mozilla/5.0 (X11; Linux x86_64)")
    hit("/status.json")
    hit("/robots.txt")
    hit("/health")
    hit("/wp-login.php", "Mozilla/5.0 (compatible; zgrab/0.1)")
    hit("/phpmyadmin/", "sqlmap/1.8.2#stable (http://sqlmap.org)")
    hit("/.env", "Mozilla/4.0 (Hydra)")
    hit("/cgi-bin/../../../../etc/passwd", "sqlmap/1.8.2#stable (http://sqlmap.org)")
    hit("/?id=1'+OR+'1'='1", "sqlmap/1.8.2#stable (http://sqlmap.org)")
    ssh_try("root", password="toor")
    ssh_try("admin", password="admin")
    if KEY.exists():
        ssh_try("operator", keyfile=KEY)


if __name__ == "__main__":
    main()
