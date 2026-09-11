#!/usr/bin/env python3
"""Учебная служба SSH: журнал попыток входа в формате syslog/sshd."""

from __future__ import annotations

import os
import socket
import sys
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = Path(os.environ.get("LAB4_LOG_DIR", ROOT / "logs"))
KEY_DIR = Path(os.environ.get("LAB4_KEY_DIR", ROOT / "keys"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
KEY_DIR.mkdir(parents=True, exist_ok=True)

AUTH_LOG = LOG_DIR / "auth.log"
HOST_KEY = KEY_DIR / "ssh_host_rsa"
OPERATOR_KEY = KEY_DIR / "operator"
BIND = os.environ.get("LAB4_SSH_HOST", "0.0.0.0")
PORT = int(os.environ.get("LAB4_SSH_PORT", "2222"))
HOST_NAME = os.environ.get("LAB4_HOSTNAME", "node")
OPERATOR = os.environ.get("LAB4_SSH_USER", "operator")
MINSK = timezone(timedelta(hours=3))

paramiko.util.log_to_file(str(LOG_DIR / "paramiko.debug"), level="ERROR")


def ensure_keys() -> tuple[paramiko.RSAKey, paramiko.RSAKey]:
    if HOST_KEY.exists():
        host = paramiko.RSAKey.from_private_key_file(str(HOST_KEY))
    else:
        host = paramiko.RSAKey.generate(2048)
        host.write_private_key_file(str(HOST_KEY))
    if OPERATOR_KEY.exists():
        user = paramiko.RSAKey.from_private_key_file(str(OPERATOR_KEY))
    else:
        user = paramiko.RSAKey.generate(2048)
        user.write_private_key_file(str(OPERATOR_KEY))
        pub = KEY_DIR / "operator.pub"
        pub.write_text(f"ssh-rsa {user.get_base64()} operator\n", encoding="utf-8")
        os.chmod(OPERATOR_KEY, 0o600)
        os.chmod(HOST_KEY, 0o600)
    return host, user


def syslog(msg: str) -> None:
    now = datetime.now(MINSK).strftime("%b %e %H:%M:%S")
    line = f"{now} {HOST_NAME} sshd[{os.getpid()}]: {msg}\n"
    with AUTH_LOG.open("a", encoding="utf-8") as fh:
        fh.write(line)


class LabServer(paramiko.ServerInterface):
    def __init__(self, peer: str, port: int, allowed: paramiko.PKey) -> None:
        self.peer = peer
        self.port = port
        self.allowed = allowed
        self.event = threading.Event()

    def check_channel_request(self, kind: str, chanid: int):  # noqa: ANN001
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username: str) -> str:
        return "publickey"

    def check_auth_password(self, username: str, password: str) -> int:
        if username != OPERATOR:
            syslog(
                f"Failed password for invalid user {username} from {self.peer} port {self.port} ssh2"
            )
        else:
            syslog(f"Failed password for {username} from {self.peer} port {self.port} ssh2")
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username: str, key: paramiko.PKey) -> int:
        if username == OPERATOR and key.get_base64() == self.allowed.get_base64():
            fp = key.get_fingerprint().hex()
            syslog(
                f"Accepted publickey for {username} from {self.peer} port {self.port} ssh2: "
                f"RSA SHA256:{fp}"
            )
            return paramiko.AUTH_SUCCESSFUL
        if username != OPERATOR:
            syslog(
                f"Failed publickey for invalid user {username} from {self.peer} port {self.port} ssh2"
            )
        else:
            syslog(f"Failed publickey for {username} from {self.peer} port {self.port} ssh2")
        return paramiko.AUTH_FAILED

    def check_channel_shell_request(self, channel):  # noqa: ANN001
        self.event.set()
        return True

    def check_channel_pty_request(self, *args) -> bool:  # noqa: ANN001
        return True


def handle(client: socket.socket, addr: tuple, host_key: paramiko.RSAKey, user_key: paramiko.RSAKey) -> None:
    peer, port = addr[0], addr[1]
    try:
        transport = paramiko.Transport(client)
        transport.local_version = "SSH-2.0-OpenSSH_9.6"
        transport.add_server_key(host_key)
        server = LabServer(peer, port, user_key)
        try:
            transport.start_server(server=server)
        except paramiko.SSHException:
            syslog(f"Did not receive identification string from {peer} port {port}")
            return
        chan = transport.accept(20)
        if chan is None:
            syslog(f"Connection closed by authenticating user from {peer} port {port}")
            return
        chan.send("доступ разрешён только к журналу событий; интерактивная оболочка не выдаётся\n")
        chan.close()
        syslog(f"Disconnected from user {OPERATOR} {peer} port {port}")
    except Exception:
        syslog(f"Connection reset by {peer} port {port}")
    finally:
        try:
            client.close()
        except OSError:
            pass


def main() -> None:
    host_key, user_key = ensure_keys()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((BIND, PORT))
    sock.listen(32)
    print(f"ssh://{BIND}:{PORT}", file=sys.stderr)
    while True:
        client, addr = sock.accept()
        threading.Thread(
            target=handle, args=(client, addr, host_key, user_key), daemon=True
        ).start()


if __name__ == "__main__":
    main()
