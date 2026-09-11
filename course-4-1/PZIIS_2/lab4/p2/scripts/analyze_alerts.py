#!/usr/bin/env python3
"""Разбор alert-файла Snort и список адресов для блокировки."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALERT = ROOT / "logs" / "alert"
OUT = ROOT / "logs" / "ids_analysis.json"
BLOCK = ROOT / "logs" / "blocklist.txt"

# 09/10-18:20:00.000000  [**] [1:1000003:1] WEB WordPress login probe [**] [Classification: ...] [Priority: 2] {TCP} 198.51.100.12:41001 -> 10.206.216.245:8088
LINE = re.compile(
    r"\[(?P<gid>\d+):(?P<sid>\d+):(?P<rev>\d+)\] (?P<msg>.+?) \[\*\*\].*?\{TCP\} "
    r"(?P<src>\d+\.\d+\.\d+\.\d+):(?P<sp>\d+) -> (?P<dst>\d+\.\d+\.\d+\.\d+):(?P<dp>\d+)"
)


def main() -> None:
    text = ALERT.read_text(encoding="utf-8", errors="replace") if ALERT.exists() else ""
    rows = []
    for line in text.splitlines():
        m = LINE.search(line)
        if not m:
            continue
        rows.append(m.groupdict())
    by_sid = Counter((r["sid"], r["msg"]) for r in rows)
    by_src = Counter(r["src"] for r in rows)
    home = {"10.206.216.10", "10.206.216.245", "127.0.0.1"}
    block = sorted(ip for ip, _n in by_src.items() if ip not in home)
    summary = {
        "alerts": len(rows),
        "by_signature": [[sid, msg, n] for (sid, msg), n in by_sid.most_common()],
        "by_src": [[ip, n] for ip, n in by_src.most_common()],
        "blocklist": block,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    BLOCK.write_text("\n".join(block) + ("\n" if block else ""), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
