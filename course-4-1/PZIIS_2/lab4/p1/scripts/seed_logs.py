#!/usr/bin/env python3
"""Сформировать журналы HTTP Combined и SSH за несколько суток."""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = Path(ROOT / "logs")
MINSK = timezone(timedelta(hours=3))
HOST = "node"

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

SCAN_UA = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (compatible; zgrab/0.1)",
    "Mozilla/5.0 (compatible; Nmap Scripting Engine)",
    "sqlmap/1.8.2#stable (http://sqlmap.org)",
    "Mozilla/4.0 (Hydra)",
    "curl/8.5.0",
    "masscan/1.3",
    "Mozilla/5.0 (compatible; DotBot/1.2)",
]

LEGIT_UA = [
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "curl/7.81.0",
]

WEB_PROBES = [
    ("GET", "/wp-login.php", 404, 412),
    ("GET", "/wp-admin/", 404, 412),
    ("GET", "/xmlrpc.php", 404, 412),
    ("GET", "/phpmyadmin/", 404, 412),
    ("GET", "/phpMyAdmin/index.php", 404, 412),
    ("GET", "/.env", 404, 412),
    ("GET", "/.git/config", 404, 412),
    ("GET", "/wp-config.php.bak", 404, 412),
    ("GET", "/admin/", 404, 412),
    ("GET", "/server-status", 404, 412),
    ("GET", "/cgi-bin/../../../../etc/passwd", 400, 390),
    ("GET", "/?id=1'+OR+'1'='1", 200, 1480),
    ("GET", "/?q=UNION+SELECT+password+FROM+users", 200, 1480),
    ("HEAD", "/", 200, 0),
]

LEGIT_HTTP = [
    ("GET", "/", 200, 1480),
    ("GET", "/status.json", 200, 96),
    ("GET", "/robots.txt", 200, 42),
    ("GET", "/health", 200, 3),
]


def ts_http(dt: datetime) -> str:
    return dt.strftime("%d/%b/%Y:%H:%M:%S %z")


def ts_ssh(dt: datetime) -> str:
    return dt.strftime("%b %e %H:%M:%S")


def combined(ip: str, dt: datetime, method: str, uri: str, status: int, length: int, ua: str, ref: str = "-") -> str:
    return (
        f'{ip} - - [{ts_http(dt)}] "{method} {uri} HTTP/1.1" {status} {length} "{ref}" "{ua}"'
    )


def ssh_line(dt: datetime, pid: int, msg: str) -> str:
    return f"{ts_ssh(dt)} {HOST} sshd[{pid}]: {msg}"


def day_range(start: datetime, days: int):
    for i in range(days):
        yield start + timedelta(days=i)


def build(days: int, end: datetime) -> tuple[list[str], list[str]]:
    rng = random.Random(401)
    start = (end - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    http: list[str] = []
    ssh: list[str] = []
    pid = 18000

    attackers_ssh = ["203.0.113.40", "203.0.113.55", "192.0.2.88"]
    attackers_web = ["198.51.100.12", "198.51.100.77", "192.0.2.88"]
    operator = "10.206.216.10"
    local = "10.206.216.245"
    users_invalid = ["admin", "ubuntu", "postgres", "oracle", "test", "pi", "ftp", "mysql"]

    for day in day_range(start, days):
        # легитимный оператор, рабочие часы
        for _ in range(rng.randint(4, 8)):
            t = day.replace(hour=rng.randint(8, 17), minute=rng.randint(0, 59), second=rng.randint(0, 59))
            method, uri, st, ln = rng.choice(LEGIT_HTTP)
            http.append(combined(operator, t, method, uri, st, ln, LEGIT_UA[0]))
        t_login = day.replace(hour=9, minute=rng.randint(0, 20), second=rng.randint(0, 59))
        pid += 1
        ssh.append(ssh_line(t_login, pid, f"Accepted publickey for operator from {operator} port {rng.randint(40000, 50000)} ssh2: RSA SHA256:lab4operator"))
        ssh.append(ssh_line(t_login + timedelta(seconds=1), pid, f"pam_unix(sshd:session): session opened for user operator(uid=1000) by (uid=0)"))
        t_out = t_login + timedelta(hours=rng.randint(2, 6), minutes=rng.randint(0, 40))
        ssh.append(ssh_line(t_out, pid, f"pam_unix(sshd:session): session closed for user operator"))
        ssh.append(ssh_line(t_out, pid, f"Disconnected from user operator {operator} port {rng.randint(40000, 50000)}"))

        # локальные проверки доступности
        for _ in range(rng.randint(2, 5)):
            t = day.replace(hour=rng.randint(7, 22), minute=rng.randint(0, 59), second=rng.randint(0, 59))
            http.append(combined(local, t, "GET", "/health", 200, 3, LEGIT_UA[2]))

        # ночной перебор SSH
        brute = attackers_ssh[0]
        night = day.replace(hour=rng.choice([1, 2, 3, 4]), minute=rng.randint(0, 40), second=0)
        for k in range(rng.randint(18, 32)):
            t = night + timedelta(seconds=k * rng.randint(2, 5))
            pid += 1
            port = 51000 + k
            ssh.append(ssh_line(t, pid, f"Failed password for root from {brute} port {port} ssh2"))
            if k % 6 == 5:
                ssh.append(ssh_line(t + timedelta(seconds=1), pid, f"Disconnecting authenticating user root {brute} port {port}: Too many authentication failures"))

        # словарь несуществующих учёток
        spray = attackers_ssh[1]
        t0 = day.replace(hour=5, minute=rng.randint(0, 30), second=0)
        for i, user in enumerate(users_invalid):
            t = t0 + timedelta(seconds=i * 7)
            pid += 1
            port = 43000 + i
            ssh.append(ssh_line(t, pid, f"Failed password for invalid user {user} from {spray} port {port} ssh2"))
            ssh.append(ssh_line(t + timedelta(seconds=1), pid, f"Invalid user {user} from {spray} port {port}"))

        # веб-сканеры CMS и секретов
        cms = attackers_web[0]
        tscan = day.replace(hour=rng.choice([0, 6, 14, 23]), minute=rng.randint(0, 50), second=0)
        for j, (method, uri, st, ln) in enumerate(WEB_PROBES):
            t = tscan + timedelta(seconds=j * 3)
            ua = SCAN_UA[j % len(SCAN_UA)]
            http.append(combined(cms, t, method, uri, st, ln, ua))

        sqli = attackers_web[1]
        t2 = day.replace(hour=21, minute=rng.randint(0, 20), second=rng.randint(0, 40))
        http.append(combined(sqli, t2, "GET", "/?id=1'+OR+'1'='1", 200, 1480, SCAN_UA[3]))
        http.append(combined(sqli, t2 + timedelta(seconds=4), "GET", "/cgi-bin/../../../../etc/passwd", 400, 390, SCAN_UA[3]))
        http.append(combined(sqli, t2 + timedelta(seconds=8), "GET", "/phpmyadmin/", 404, 412, SCAN_UA[3]))

        # корреляция: тот же адрес бьёт и в SSH, и в HTTP
        both = attackers_web[2]
        t3 = day.replace(hour=18, minute=rng.randint(0, 15), second=0)
        pid += 1
        ssh.append(ssh_line(t3, pid, f"Failed password for invalid user admin from {both} port 44101 ssh2"))
        ssh.append(ssh_line(t3 + timedelta(seconds=2), pid, f"Failed password for root from {both} port 44101 ssh2"))
        http.append(combined(both, t3 + timedelta(seconds=6), "GET", "/.env", 404, 412, SCAN_UA[4]))
        http.append(combined(both, t3 + timedelta(seconds=9), "GET", "/wp-login.php", 404, 412, SCAN_UA[4]))

        # мусор идентификации SSH
        if rng.random() < 0.7:
            t4 = day.replace(hour=3, minute=12, second=rng.randint(0, 59))
            pid += 1
            ssh.append(ssh_line(t4, pid, f"Did not receive identification string from 198.51.100.200 port {rng.randint(10000, 60000)}"))

    http.sort(key=lambda s: s.split("[")[1][:20])
    ssh.sort(key=lambda s: s[:15])
    return http, ssh


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    args = parser.parse_args()
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    end = datetime(2026, 9, 10, 18, 0, 0, tzinfo=MINSK)
    http, ssh = build(args.days, end)
    (LOG_DIR / "access.log").write_text("\n".join(http) + "\n", encoding="utf-8")
    err = []
    for line in http:
        if " 404 " not in line and " 400 " not in line:
            continue
        ip = line.split()[0]
        stamp = line.split("[")[1].split("]")[0]
        dt = datetime.strptime(stamp, "%d/%b/%Y:%H:%M:%S %z")
        uri = line.split('"')[1].split()[1]
        status = line.split('"')[2].split()[0]
        err.append(f"[{dt.strftime('%a %b %d %H:%M:%S %Y')}] [client {ip}] {status} for {uri}")
    (LOG_DIR / "error.log").write_text("\n".join(err) + "\n", encoding="utf-8")
    (LOG_DIR / "auth.log").write_text("\n".join(ssh) + "\n", encoding="utf-8")
    print(f"HTTP {len(http)} строк, SSH {len(ssh)} строк, error {len(err)}")


if __name__ == "__main__":
    main()
