import base64
import io
import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import CORPUS_DIR, EXPORT_DIR
from .db import fetch_all

plt.rcParams["font.family"] = "DejaVu Sans"

METHODS = ("weighted", "baseline")
LABELS = {
    "weighted": "По весу",
    "baseline": "Первые 10",
}


def prf(got, gold):
    hit = got & gold
    p = len(hit) / len(got) if got else 0.0
    r = len(hit) / len(gold) if gold else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return {
        "precision": round(p, 3),
        "recall": round(r, 3),
        "f1": round(f1, 3),
        "correct": got == gold,
    }


def avg(rows, key):
    vals = [row[key] for row in rows if row.get(key) is not None]
    if not vals:
        return 0.0
    return round(sum(vals) / len(vals), 3)


def load_gold():
    data = json.loads((CORPUS_DIR / "manifest.json").read_text(encoding="utf-8"))
    out = {}
    for item in data:
        out[item["file"]] = item.get("gold", [])
    return out


def evaluate():
    gold = load_gold()
    rows = fetch_all(
        """
        SELECT title, language, domain, source_file, elapsed_ms,
               selected_json, baseline_selected
        FROM documents
        ORDER BY id
        """
    )
    docs = []
    by_method = {k: [] for k in METHODS}
    by_lang = defaultdict(list)
    by_dom = defaultdict(list)

    for row in rows:
        need = set(gold.get(row["source_file"] or "", []))
        if not need:
            continue
        got = set(row["selected_json"] or [])
        base = set(row["baseline_selected"] or [])
        m1 = prf(got, need)
        m2 = prf(base, need)
        item = {
            "title": row["title"],
            "language": row["language"],
            "domain": row["domain"],
            "source_file": row["source_file"],
            "elapsed_ms": row["elapsed_ms"],
            "gold": sorted(need),
            "selected": sorted(got),
            "baseline_selected": sorted(base),
            "weighted": m1,
            "baseline": m2,
        }
        docs.append(item)
        by_method["weighted"].append({**m1, "elapsed_ms": row["elapsed_ms"]})
        by_method["baseline"].append({**m2, "elapsed_ms": 0})
        by_lang[row["language"]].append(m1)
        by_dom[row["domain"]].append(m1)

    cmp_rows = []
    for k in METHODS:
        items = by_method[k]
        cmp_rows.append({
            "model": k,
            "label": LABELS[k],
            "precision": avg(items, "precision"),
            "recall": avg(items, "recall"),
            "f1": avg(items, "f1"),
            "avg_elapsed_ms": avg(items, "elapsed_ms"),
        })

    groups = {
        "language": {},
        "domain": {},
    }
    for name, items in by_lang.items():
        groups["language"][name] = {
            "precision": avg(items, "precision"),
            "recall": avg(items, "recall"),
            "f1": avg(items, "f1"),
        }
    for name, items in by_dom.items():
        groups["domain"][name] = {
            "precision": avg(items, "precision"),
            "recall": avg(items, "recall"),
            "f1": avg(items, "f1"),
        }

    return {
        "documents": docs,
        "comparison": cmp_rows,
        "groups": groups,
        "main": cmp_rows[0] if cmp_rows else {},
    }


def build_charts(data, export_dir=None):
    export_dir = Path(export_dir or EXPORT_DIR)
    export_dir.mkdir(parents=True, exist_ok=True)
    charts = {}
    docs = data.get("documents") or []
    if not docs:
        return charts

    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    xs = range(len(docs))
    ax.bar([i - 0.18 for i in xs], [d["weighted"]["f1"] for d in docs], width=0.36, label="По весу")
    ax.bar([i + 0.18 for i in xs], [d["baseline"]["f1"] for d in docs], width=0.36, label="Первые 10")
    ax.set_xticks(list(xs))
    ax.set_xticklabels([d["title"][:28] for d in docs], rotation=18, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("F1")
    ax.set_title("F1 по документам")
    ax.legend()
    fig.tight_layout()
    charts["metrics_by_doc"] = dump_fig(fig, export_dir / "metrics_by_doc.png")

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    names = [r["label"] for r in data["comparison"]]
    vals = [r["f1"] for r in data["comparison"]]
    ax.bar(names, vals, color=["#2f6fed", "#8aa0c2"])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("F1")
    ax.set_title("Методы")
    fig.tight_layout()
    charts["method_comparison"] = dump_fig(fig, export_dir / "method_comparison.png")

    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.bar([d["title"][:22] for d in docs], [d["elapsed_ms"] for d in docs], color="#2f6fed")
    ax.set_ylabel("мс")
    ax.set_title("Время")
    fig.autofmt_xdate(rotation=18)
    fig.tight_layout()
    charts["time_comparison"] = dump_fig(fig, export_dir / "time_comparison.png")
    return charts


def dump_fig(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=140)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")
