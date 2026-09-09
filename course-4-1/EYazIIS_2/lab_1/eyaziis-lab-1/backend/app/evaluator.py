import base64
import io
import json
import logging
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import DEFAULT_TOP_K, EXPORT_DIR
from .db import execute, fetch_all
from .search_service import retrieve_ids

log = logging.getLogger(__name__)

RECALL_LEVELS = [round(0.1 * i, 1) for i in range(11)]

MODELS = {
    "bm25": {"model": "bm25", "use_prf": False, "label": "BM25"},
    "bm25_prf": {"model": "bm25", "use_prf": True, "label": "BM25 + PRF"},
    "tfidf": {"model": "tfidf", "use_prf": False, "label": "TF-IDF"},
}

PRIMARY_MODEL = "bm25"


def _f_measure(precision: float, recall: float, beta: float) -> float:
    if precision == 0 and recall == 0:
        return 0.0
    beta_sq = beta * beta
    return (1 + beta_sq) * precision * recall / (beta_sq * precision + recall)


def _average_precision(retrieved: list[int], relevant: set[int]) -> float:
    if not relevant:
        return 0.0
    hits = 0
    total = 0.0
    for position, doc_id in enumerate(retrieved, start=1):
        if doc_id in relevant:
            hits += 1
            total += hits / position
    return total / len(relevant)


def _ndcg(retrieved: list[int], relevant: set[int], k: int) -> float:
    gains = [1.0 if doc_id in relevant else 0.0 for doc_id in retrieved[:k]]
    dcg = sum(gain / math.log2(position + 1) for position, gain in enumerate(gains, start=1))
    ideal_hits = min(len(relevant), k)
    idcg = sum(1.0 / math.log2(position + 1) for position in range(1, ideal_hits + 1))
    return dcg / idcg if idcg else 0.0


def _precision_at(retrieved: list[int], relevant: set[int], k: int) -> float:
    if k == 0:
        return 0.0
    window = retrieved[:k]
    return sum(1 for doc_id in window if doc_id in relevant) / k


def _interpolated_precision(retrieved: list[int], relevant: set[int]) -> list[float]:
    if not relevant:
        return [0.0] * len(RECALL_LEVELS)

    points: list[tuple[float, float]] = []
    hits = 0
    for position, doc_id in enumerate(retrieved, start=1):
        if doc_id in relevant:
            hits += 1
            points.append((hits / len(relevant), hits / position))

    interpolated = []
    for level in RECALL_LEVELS:
        candidates = [precision for recall, precision in points if recall >= level]
        interpolated.append(max(candidates) if candidates else 0.0)
    return interpolated


def _load_gold_standard() -> list[dict]:
    rows = fetch_all(
        """
        SELECT q.id, q.code, q.query, q.comment,
               COALESCE(array_agg(d.id) FILTER (WHERE d.id IS NOT NULL), '{}') AS relevant
        FROM eval_queries q
        LEFT JOIN eval_qrels r ON r.query_id = q.id
        LEFT JOIN documents d ON d.source_file = r.source_file
        GROUP BY q.id, q.code, q.query, q.comment
        ORDER BY q.code
        """
    )
    return rows


def evaluate(model_key: str = PRIMARY_MODEL, top_k: int = DEFAULT_TOP_K) -> dict:
    settings = MODELS[model_key]
    gold = _load_gold_standard()

    per_query: list[dict] = []
    curves: list[list[float]] = []

    for item in gold:
        relevant = set(item["relevant"])
        retrieved = retrieve_ids(
            item["query"], top_k=top_k, model=settings["model"], use_prf=settings["use_prf"]
        )
        found = [doc_id for doc_id in retrieved if doc_id in relevant]

        precision = len(found) / len(retrieved) if retrieved else 0.0
        recall = len(found) / len(relevant) if relevant else 0.0

        per_query.append(
            {
                "code": item["code"],
                "query": item["query"],
                "comment": item["comment"],
                "relevant_count": len(relevant),
                "retrieved_count": len(retrieved),
                "precision": precision,
                "recall": recall,
                "f1": _f_measure(precision, recall, 1.0),
                "f05": _f_measure(precision, recall, 0.5),
                "f2": _f_measure(precision, recall, 2.0),
                "p5": _precision_at(retrieved, relevant, 5),
                "p10": _precision_at(retrieved, relevant, 10),
                "r_precision": _precision_at(retrieved, relevant, len(relevant)),
                "average_precision": _average_precision(retrieved, relevant),
                "ndcg10": _ndcg(retrieved, relevant, 10),
            }
        )
        curves.append(_interpolated_precision(retrieved, relevant))

    def mean(field: str) -> float:
        return sum(row[field] for row in per_query) / len(per_query) if per_query else 0.0

    curve = [
        sum(values[i] for values in curves) / len(curves) if curves else 0.0
        for i in range(len(RECALL_LEVELS))
    ]

    summary = {
        "model": model_key,
        "label": settings["label"],
        "top_k": top_k,
        "queries": len(per_query),
        "precision": mean("precision"),
        "recall": mean("recall"),
        "f1": mean("f1"),
        "f05": mean("f05"),
        "f2": mean("f2"),
        "p5": mean("p5"),
        "p10": mean("p10"),
        "r_precision": mean("r_precision"),
        "map": mean("average_precision"),
        "ndcg10": mean("ndcg10"),
    }

    execute(
        "INSERT INTO eval_runs (model, top_k, summary) VALUES (%s, %s, %s)",
        (model_key, top_k, json.dumps(summary, ensure_ascii=False)),
    )

    return {
        "summary": summary,
        "per_query": per_query,
        "recall_levels": RECALL_LEVELS,
        "pr_curve": curve,
    }


def compare_models(top_k: int = DEFAULT_TOP_K) -> dict:
    return {key: evaluate(key, top_k=top_k) for key in MODELS}


def _figure_to_png(fig, target: Path | None) -> str:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    data = buffer.getvalue()
    if target is not None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return base64.b64encode(data).decode("ascii")


def chart_metrics_by_query(evaluation: dict, target: Path | None = None) -> str:
    rows = evaluation["per_query"]
    codes = [row["code"] for row in rows]
    positions = range(len(rows))
    width = 0.27

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar([p - width for p in positions], [r["precision"] for r in rows], width, label="Точность")
    ax.bar(list(positions), [r["recall"] for r in rows], width, label="Полнота")
    ax.bar([p + width for p in positions], [r["f1"] for r in rows], width, label="F1-мера")

    ax.set_xticks(list(positions))
    ax.set_xticklabels(codes, rotation=0)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Эталонный запрос")
    ax.set_ylabel("Значение метрики")
    ax.set_title(f"Качество поиска по запросам ({evaluation['summary']['label']})")
    ax.legend(loc="lower right")
    ax.grid(axis="y", linestyle=":", alpha=0.6)

    return _figure_to_png(fig, target)


def chart_pr_curve(evaluations: dict[str, dict], target: Path | None = None) -> str:
    styles = [
        {"linestyle": "-", "marker": "o", "linewidth": 3.5, "markersize": 9, "alpha": 0.9},
        {"linestyle": "--", "marker": "s", "linewidth": 2.2, "markersize": 7, "alpha": 0.9},
        {"linestyle": ":", "marker": "^", "linewidth": 1.6, "markersize": 5, "alpha": 1.0},
    ]

    fig, ax = plt.subplots(figsize=(7, 5))
    for style, evaluation in zip(styles, evaluations.values()):
        ax.plot(
            evaluation["recall_levels"],
            evaluation["pr_curve"],
            label=evaluation["summary"]["label"],
            **style,
        )
    ax.set_xlabel("Полнота")
    ax.set_ylabel("Точность (интерполированная)")
    ax.set_title("11-точечная кривая полноты-точности")
    ax.set_ylim(0, 1.05)
    ax.grid(linestyle=":", alpha=0.6)
    ax.legend()
    return _figure_to_png(fig, target)


def chart_model_comparison(evaluations: dict[str, dict], target: Path | None = None) -> str:
    metric_names = ["precision", "recall", "f1", "p5", "map", "ndcg10"]
    metric_labels = ["Точность", "Полнота", "F1", "P@5", "MAP", "nDCG@10"]
    width = 0.26

    fig, ax = plt.subplots(figsize=(9, 4.5))
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
    ax.set_title("Сравнение моделей ранжирования")
    ax.legend()
    ax.grid(axis="y", linestyle=":", alpha=0.6)

    return _figure_to_png(fig, target)


def build_charts(evaluations: dict[str, dict], export_dir: Path | None = None) -> dict[str, str]:
    main = evaluations[PRIMARY_MODEL]
    return {
        "metrics_by_query": chart_metrics_by_query(
            main, export_dir / "metrics_by_query.png" if export_dir else None
        ),
        "pr_curve": chart_pr_curve(
            evaluations, export_dir / "pr_curve.png" if export_dir else None
        ),
        "model_comparison": chart_model_comparison(
            evaluations, export_dir / "model_comparison.png" if export_dir else None
        ),
    }


def _print_report(evaluations: dict[str, dict]) -> None:
    main = evaluations[PRIMARY_MODEL]
    print(f"{'Запрос':<38}{'P':>7}{'R':>7}{'F1':>7}{'P@5':>7}{'AP':>7}{'nDCG':>7}")
    for row in main["per_query"]:
        print(
            f"{row['query'][:37]:<38}"
            f"{row['precision']:>7.3f}{row['recall']:>7.3f}{row['f1']:>7.3f}"
            f"{row['p5']:>7.3f}{row['average_precision']:>7.3f}{row['ndcg10']:>7.3f}"
        )
    print("-" * 80)
    for evaluation in evaluations.values():
        summary = evaluation["summary"]
        print(
            f"{summary['label']:<38}"
            f"{summary['precision']:>7.3f}{summary['recall']:>7.3f}{summary['f1']:>7.3f}"
            f"{summary['p5']:>7.3f}{summary['map']:>7.3f}{summary['ndcg10']:>7.3f}"
        )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Оценка качества работы ИПС")
    parser.add_argument("--export", type=Path, default=None, help="каталог для сохранения графиков")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K, help="глубина выдачи")
    parser.add_argument("--json", type=Path, default=None, help="файл для выгрузки метрик в JSON")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    evaluations = compare_models(top_k=args.top_k)
    _print_report(evaluations)

    export_dir = args.export or EXPORT_DIR
    if export_dir:
        build_charts(evaluations, export_dir=Path(export_dir))
        print(f"\nГрафики сохранены в {export_dir}")

    if args.json:
        args.json.write_text(
            json.dumps(
                {key: value["summary"] for key, value in evaluations.items()}
                | {"per_query": evaluations[PRIMARY_MODEL]["per_query"]},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
