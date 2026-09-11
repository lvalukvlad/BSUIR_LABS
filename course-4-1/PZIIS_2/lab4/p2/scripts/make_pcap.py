#!/usr/bin/env python3
"""Собрать pcap с типичными запросами к HTTP:8088 и SYN на SSH:2222."""

from __future__ import annotations

import struct
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pcaps" / "lab4.pcap"
DST_IP = bytes([10, 206, 216, 245])


def ip_to_bytes(dotted: str) -> bytes:
    return bytes(int(p) for p in dotted.split("."))


def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"
    s = sum(struct.unpack("!" + "H" * (len(data) // 2), data))
    s = (s >> 16) + (s & 0xFFFF)
    s += s >> 16
    return (~s) & 0xFFFF


def ipv4(src: bytes, dst: bytes, payload: bytes, proto: int = 6) -> bytes:
    total = 20 + len(payload)
    hdr = struct.pack(
        "!BBHHHBBH4s4s",
        0x45,
        0,
        total,
        0x3941,
        0,
        64,
        proto,
        0,
        src,
        dst,
    )
    csum = checksum(hdr)
    return hdr[:10] + struct.pack("!H", csum) + hdr[12:] + payload


def tcp(src_port: int, dst_port: int, flags: int, payload: bytes, src_ip: bytes, dst_ip: bytes) -> bytes:
    offset = 5 << 4
    base = struct.pack("!HHIIBBHHH", src_port, dst_port, 1000, 0, offset, flags, 8192, 0, 0)
    pseudo = src_ip + dst_ip + struct.pack("!BBH", 0, 6, len(base) + len(payload))
    csum = checksum(pseudo + base + payload)
    return base[:16] + struct.pack("!H", csum) + base[18:] + payload


def frame(src_ip: str, src_port: int, dst_port: int, flags: int, payload: bytes) -> bytes:
    src = ip_to_bytes(src_ip)
    body = tcp(src_port, dst_port, flags, payload, src, DST_IP)
    eth = b"\x00\x11\x22\x33\x44\x55" + b"\x66\x77\x88\x99\xaa\xbb" + b"\x08\x00"
    return eth + ipv4(src, DST_IP, body)


def rec(pkt: bytes, ts: float) -> bytes:
    sec = int(ts)
    usec = int((ts - sec) * 1_000_000)
    return struct.pack("=IIII", sec, usec, len(pkt), len(pkt)) + pkt


def http_payload(path: str, ua: str, host: str = "10.206.216.245:8088") -> bytes:
    return (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: {ua}\r\n"
        f"Accept: */*\r\n"
        f"\r\n"
    ).encode("ascii", errors="replace")


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    ts = time.mktime(time.strptime("10/09/2026 18:20:00", "%d/%m/%Y %H:%M:%S"))
    samples = [
        ("198.51.100.12", 41001, 8088, 0x18, http_payload("/wp-login.php", "Mozilla/5.0 (compatible; zgrab/0.1)")),
        ("198.51.100.12", 41002, 8088, 0x18, http_payload("/phpmyadmin/", "Mozilla/5.0")),
        ("198.51.100.77", 41003, 8088, 0x18, http_payload("/cgi-bin/../../../../etc/passwd", "sqlmap/1.8.2#stable (http://sqlmap.org)")),
        ("198.51.100.77", 41004, 8088, 0x18, http_payload("/?id=1'+OR+'1'='1", "sqlmap/1.8.2#stable (http://sqlmap.org)")),
        ("192.0.2.88", 41005, 8088, 0x18, http_payload("/.env", "Mozilla/4.0 (Hydra)")),
        ("192.0.2.88", 41006, 8088, 0x18, http_payload("/", "Mozilla/4.0 (Hydra)")),
        ("203.0.113.40", 51022, 2222, 0x02, b""),
        ("203.0.113.40", 51023, 2222, 0x02, b""),
        ("10.206.216.10", 40011, 8088, 0x18, http_payload("/", "Mozilla/5.0 (X11; Linux x86_64)")),
    ]
    hdr = struct.pack("=IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)
    blobs = [
        rec(frame(src, sport, dport, flags, payload), ts + i)
        for i, (src, sport, dport, flags, payload) in enumerate(samples)
    ]
    OUT.write_bytes(hdr + b"".join(blobs))
    print(f"pcap {OUT} ({OUT.stat().st_size} байт, {len(samples)} кадров)")


if __name__ == "__main__":
    main()
