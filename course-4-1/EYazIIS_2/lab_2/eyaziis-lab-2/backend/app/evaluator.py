import base64
import io
import json
import logging
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import EXPORT_DIR
from .db import execute, fetch_all
from .language_model import FrequentWordsRecognizer, NeuralNetworkRecognizer, ShortWordsRecognizer
from .text_processing import reset_preprocess_cache

log = logging.getLogger(__name__)

plt.rcParams["font.family"] = "DejaVu Sans"

METHODS = ["short_words", "frequent_words", "neural_network"]
PRIMARY_MODEL = "neural_network"


def _f_measure(precision: float, recall: float, beta: float) -> float:
    if precision == 0 and recall == 0:
        return 0.0
    beta_sq = beta * beta
    return (1 + beta_sq) * precision * recall / (beta_sq * precision + recall)


def _method_label(key: str) -> str:
    return {
        "short_words": "Коротких слов",
        "frequent_words": "Частотных слов",
        "neural_network": "Нейросетевой",
    }[key]


def _load_gold_standard() -> list[dict]:
    return fetch_all(
        """
        SELECT q.code, q.query, q.text, q.relevant
        FROM eval_queries q
        ORDER BY q.code
        """
    )


def _get_recognizers() -> dict:
    from .bootstrap import get_runtime

    runtime = get_runtime()
    return {
        "short": ShortWordsRecognizer(),
        "freq": FrequentWordsRecognizer(),
        "nn": runtime["nn"],
        "profiles": {
            "short_words": {
                language: methods.get("short_words", {})
                for language, methods in runtime["profiles"].items()
            },
            "frequent_words": {
                language: methods.get("frequent_words", {})
                for language, methods in runtime["profiles"].items()
            },
        },
    }


def _recognize_with_method(text: str, method: str, recognizers: dict) -> dict:
    if method in {"short_words", "frequent_words"}:
        reset_preprocess_cache()
    if method == "short_words":
        return recognizers["short"].recognize(text, recognizers["profiles"]["short_words"])
    if method == "frequent_words":
        return recognizers["freq"].recognize(text, recognizers["profiles"]["frequent_words"])
    if method == "neural_network":
        return recognizers["nn"].recognize(text)
    return {"language": "unknown", "confidence": 0.0}


def evaluate(model_key: str = PRIMARY_MODEL) -> dict:
    gold = _load_gold_standard()
    recognizers = _get_recognizers()

    per_query = []
    started_all = time.perf_counter()
    for item in gold:
        started = time.perf_counter()
        result = _recognize_with_method(item["text"], model_key, recognizers)
        elapsed = (time.perf_counter() - started) * 1000
        predicted = set(result.get("languages") or [])
        relevant = set(item["relevant"] or [])
        inter = predicted & relevant
        precision = len(inter) / len(predicted) if predicted else 0.0
        recall = len(inter) / len(relevant) if relevant else 0.0
        correct = predicted == relevant
        per_query.append(
            {
                "code": item["code"],
                "query": item["query"],
                "predicted": sorted(predicted),
                "relevant": sorted(relevant),
                "correct": correct,
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "confidence": float(result.get("confidence") or 0.0),
                "elapsed_ms": round(elapsed, 2),
            }
        )
    total_ms = (time.perf_counter() - started_all) * 1000

    total = len(per_query)
    correct_count = sum(1 for row in per_query if row["correct"])
    accuracy = correct_count / total if total else 0.0
    precision = sum(row["precision"] for row in per_query) / total if total else 0.0
    recall = sum(row["recall"] for row in per_query) / total if total else 0.0

    summary = {
        "model": model_key,
        "label": _method_label(model_key),
        "queries": total,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": _f_measure(precision, recall, 1.0),
        "f05": _f_measure(precision, recall, 0.5),
        "f2": _f_measure(precision, recall, 2.0),
        "correct": correct_count,
        "elapsed_ms": round(total_ms, 2),
        "avg_elapsed_ms": round(total_ms / total, 2) if total else 0.0,
    }

    execute(
        "INSERT INTO eval_runs (model, top_k, summary) VALUES (%s, %s, %s)",
        (model_key, total, json.dumps(summary, ensure_ascii=False)),
    )
    return {"summary": summary, "per_query": per_query}


def compare_methods() -> dict:
    return {key: evaluate(key) for key in METHODS}


def _figure_to_png(fig, target: Path | None) -> str:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    data = buffer.getvalue()
    if target is not None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return base64.b64encode(data).decode("ascii")


def chart_method_comparison(evaluations: dict, target: Path | None = None) -> str:
    metric_names = ["accuracy", "precision", "recall", "f1"]
    metric_labels = ["Accuracy", "Точность", "Полнота", "F1"]
    width = 0.24

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    for index, evaluation in enumerate(evaluations.values()):
        summary = evaluation["summary"]
        offset = (index - 1) * width
        ax.bar(
            [i + offset for i in range(len(metric_names))],
            [summary[name] for name in metric_names],
            width,
            label=summary["label"],
        )
    ax.set_xticks(range(len(metric_names)))
    ax.set_xticklabels(metric_labels)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Среднее значение")
    ax.set_title("Сравнение методов распознавания языка")
    ax.legend()
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    return _figure_to_png(fig, target)


def chart_time_comparison(evaluations: dict, target: Path | None = None) -> str:
    labels = [item["summary"]["label"] for item in evaluations.values()]
    times = [item["summary"]["avg_elapsed_ms"] for item in evaluations.values()]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(labels, times, color=["#2f6fed", "#e05b5b", "#4caf50"])
    ax.set_ylabel("Среднее время, мс")
    ax.set_title("Быстродействие методов распознавания")
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    for bar, value in zip(bars, times):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.1f}", ha="center", va="bottom")
    return _figure_to_png(fig, target)


def chart_metrics_by_query(evaluation: dict, target: Path | None = None) -> str:
    rows = evaluation["per_query"]
    codes = [row["code"] for row in rows]
    values = [1.0 if row["correct"] else 0.0 for row in rows]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(codes, values, color=["#4caf50" if value else "#e05b5b" for value in values])
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Верно / неверно")
    ax.set_title(f"Распознавание эталонных текстов ({evaluation['summary']['label']})")
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    return _figure_to_png(fig, target)


def build_charts(evaluations: dict, export_dir: Path | None = None) -> dict[str, str]:
    main = evaluations[PRIMARY_MODEL]
    return {
        "method_comparison": chart_method_comparison(
            evaluations, export_dir / "method_comparison.png" if export_dir else None
        ),
        "time_comparison": chart_time_comparison(
            evaluations, export_dir / "time_comparison.png" if export_dir else None
        ),
        "metrics_by_query": chart_metrics_by_query(
            main, export_dir / "metrics_by_query.png" if export_dir else None
        ),
    }


def _print_report(evaluations: dict) -> None:
    print(f"{'Метод':<22}{'Acc':>8}{'P':>8}{'R':>8}{'F1':>8}{'мс':>10}")
    for evaluation in evaluations.values():
        summary = evaluation["summary"]
        print(
            f"{summary['label']:<22}"
            f"{summary['accuracy']:>8.3f}{summary['precision']:>8.3f}"
            f"{summary['recall']:>8.3f}{summary['f1']:>8.3f}"
            f"{summary['avg_elapsed_ms']:>10.2f}"
        )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Оценка качества распознавания языка")
    parser.add_argument("--export", type=Path, default=None)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    from .db import init_pool
    from .migrate import run_migrations

    init_pool()
    run_migrations()

    evaluations = compare_methods()
    _print_report(evaluations)
    export_dir = args.export or EXPORT_DIR
    if export_dir:
        build_charts(evaluations, export_dir=Path(export_dir))
        print(f"Графики сохранены в {export_dir}")
    if args.json:
        args.json.write_text(
            json.dumps({key: value["summary"] for key, value in evaluations.items()}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
