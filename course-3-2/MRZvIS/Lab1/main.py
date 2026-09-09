# Лабораторная работа №1
# МРЗвИС — конвейерная обработка потока; попарное умножение векторов
#
# Автор: студент гр. 321701, Лукашов Владислав Андреевич
# Вариант 15: умножение p-разрядных чисел со старших разрядов множителя,
#             множимое после каждого бита сдвигается вправо (беззнаковые).
#
# Источник постановки: лабораторный практикум по МРЗвИС.

from __future__ import annotations

import functools
import os
import random
import sys
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Константы оформления
# ---------------------------------------------------------------------------

CONSOLE_WIDTH = 80
GRAPH_DPI = 130
GRAPH_FILENAME = "graphs_lab1.png"
DAT_PREFIX = "lab1_curve"  # при сохранении графиков пишутся и .dat для отчёта


# ---------------------------------------------------------------------------
# Двоичное представление (группы по 4 бита, как в методичке)
# ---------------------------------------------------------------------------


def bin_groups(value: int, bit_width: int) -> str:
    mask = (1 << bit_width) - 1
    bits = f"{value & mask:0{bit_width}b}"
    return " ".join(bits[i : i + 4] for i in range(0, len(bits), 4))


@functools.lru_cache(maxsize=128)
def _bit_positions_per_stage(stage_count: int, p: int) -> Tuple[Tuple[int, ...], ...]:
    """Раскладка битов множителя [p-1..0] по этапам (детерминировано от n и p)."""
    order = tuple(range(p - 1, -1, -1))
    if stage_count == 1:
        return (order,)
    buckets: List[List[int]] = [[] for _ in range(stage_count)]
    for k, pos in enumerate(order):
        buckets[(k * stage_count) // p].append(pos)
    return tuple(tuple(b) for b in buckets)


# ---------------------------------------------------------------------------
# Состояние пары на конвейере
# ---------------------------------------------------------------------------


def _new_work_item(a: int, b: int, p: int) -> dict:
    return {
        "idx": None,
        "a": a,
        "b": b,
        "mul": a << (p - 1),
        "acc": 0,
        "bits_done": 0,
        "result": 0,
        "t_enter": 0,
    }


def _apply_stage_bits(work: dict, positions: Sequence[int], p: int) -> None:
    b = work["b"]
    for pos in positions:
        if (b >> pos) & 1:
            work["acc"] += work["mul"]
        work["mul"] >>= 1
        work["bits_done"] += 1
    if work["bits_done"] >= p:
        work["result"] = work["acc"]


# ---------------------------------------------------------------------------
# Один такт конвейера
# ---------------------------------------------------------------------------


@dataclass
class StageSlot:
    work: dict
    time_left: int
    ready: bool


def _tick(
    clock: int,
    slots: List[Optional[StageSlot]],
    ti: Sequence[int],
    stage_bits: Tuple[Tuple[int, ...], ...],
    p: int,
    queue: Sequence[Tuple[int, int]],
    next_idx: int,
    launch_gap: int,
    results: List[dict],
) -> Tuple[int, int, bool]:
    """Один глобальный такт. Возвращает (clock, next_idx, finished)."""
    clock += 1
    n_stages = len(slots)

    for cell in slots:
        if cell is not None and cell.time_left > 0:
            cell.time_left -= 1

    for idx in range(n_stages - 1, -1, -1):
        cell = slots[idx]
        if cell is None or cell.time_left > 0:
            continue
        w = cell.work
        if not cell.ready:
            _apply_stage_bits(w, stage_bits[idx], p)
            cell.ready = True

        if idx == n_stages - 1:
            results.append(
                {
                    "i": w["idx"],
                    "a": w["a"],
                    "b": w["b"],
                    "c": w["result"],
                    "t": clock,
                }
            )
            slots[idx] = None
            continue

        if slots[idx + 1] is not None:
            continue
        slots[idx + 1] = StageSlot(work=w, time_left=ti[idx + 1], ready=False)
        slots[idx] = None

    if next_idx < len(queue) and slots[0] is None and clock >= 1 + next_idx * launch_gap:
        a, b = queue[next_idx]
        w = _new_work_item(a, b, p)
        w["idx"] = next_idx
        w["t_enter"] = clock
        slots[0] = StageSlot(work=w, time_left=ti[0], ready=False)
        next_idx += 1

    return clock, next_idx, len(results) >= len(queue)


def simulate(
    queue: Sequence[Tuple[int, int]],
    ti: Sequence[int],
    p: int,
    n_stages: int,
    launch_gap: int,
    *,
    visualize: bool,
) -> Tuple[int, List[dict]]:
    """
    Полный прогон. visualize=True — очистка экрана и картинка на каждом такте
    (медленно, для отладки); False — только счёт (быстро).
    """
    if len(ti) != n_stages:
        raise ValueError("длина ti должна совпадать с числом этапов n")
    stage_bits = _bit_positions_per_stage(n_stages, p)
    slots: List[Optional[StageSlot]] = [None] * n_stages
    results: List[dict] = []
    next_idx = 0
    clock = 0
    sum_ti = sum(ti)
    tick_limit = len(queue) * (sum_ti + 5) * 12

    while len(results) < len(queue):
        clock, next_idx, done = _tick(
            clock, slots, ti, stage_bits, p, queue, next_idx, launch_gap, results
        )
        if visualize:
            _render(clock, slots, ti, p, results, n_stages)
            input("\n>>> Enter — следующий такт ")
        if clock > tick_limit:
            raise RuntimeError("превышен лимит тактов: проверьте n, r, m, p и ti")
        if done:
            break

    return clock, results


# ---------------------------------------------------------------------------
# Визуализация
# ---------------------------------------------------------------------------


def _clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    os.system("")  # сброс артефактов в некоторых терминалах


def _render(
    tick: int,
    slots: Sequence[Optional[StageSlot]],
    ti: Sequence[int],
    p: int,
    results: Iterable[dict],
    n_stages: int,
) -> None:
    _clear_screen()
    line = f"=== ТАКТ {tick} "
    print(line + "=" * max(0, CONSOLE_WIDTH - len(line)))
    head = f"{'Этап':<8} | {'Пара':^5} | {'ti':^6} | {'Бит':^5} | Данные"
    print(head)
    print("-" * CONSOLE_WIDTH)

    acc_w = 2 * p
    mul_w = 2 * p
    for k in range(n_stages):
        label = f"S{k + 1}"
        cell = slots[k]
        if cell is None:
            print(f"{label:<8} | {'—':^5} | {'—':^6} | {'—':^5} | [свободен]")
            continue
        w = cell.work
        tau = max(0, tick - w["t_enter"])
        if cell.time_left > 0:
            ti_cell = f"{cell.time_left}/{ti[k]}"
        else:
            ti_cell = "—"
        body = (
            f"τ={tau} | B={bin_groups(w['b'], p)} | "
            f"mul={bin_groups(w['mul'], mul_w)} | acc={bin_groups(w['acc'], acc_w)}"
        )
        print(
            f"{label:<8} | {str(w['idx'] if w['idx'] is not None else '—'):^5} | "
            f"{ti_cell:^6} | {w['bits_done']}/{p} | {body}"
        )

    print("-" * CONSOLE_WIDTH)
    tail = sorted(results, key=lambda r: r["i"])
    if tail:
        print("Готовые пары (десятичн., такт готовности):")
        for row in tail[-10:]:
            print(
                f"  idx {row['i']}: A={row['a']} B={row['b']} → C={row['c']} @ t={row['t']}"
            )


# ---------------------------------------------------------------------------
# Проверка и теория (S, E)
# ---------------------------------------------------------------------------


def verify(queue: Sequence[Tuple[int, int]], results: Sequence[dict]) -> List[Tuple[int, int, int]]:
    """Возвращает список ошибок (idx, ожидалось, получено); idx < 0 — структурная ошибка."""
    bad: List[Tuple[int, int, int]] = []
    if len(results) != len(queue):
        bad.append((-1, len(queue), len(results)))
        return bad
    seen: set[int] = set()
    for row in results:
        i = row["i"]
        if i in seen:
            bad.append((i, -1, -1))
            continue
        seen.add(i)
        if i < 0 or i >= len(queue):
            bad.append((i, -1, row["c"]))
            continue
        exp = queue[i][0] * queue[i][1]
        if row["c"] != exp:
            bad.append((i, exp, row["c"]))
    if seen != set(range(len(queue))):
        bad.append((-2, len(queue), len(seen)))
    return bad


def theoretical_metrics(
    n_stages: int, pair_count: int, launch_gap: int, ti: Sequence[int]
) -> Tuple[float, float, float, float]:
    """T_seq, T_pipe, S, E (теория по сбалансированной оценке из практикума)."""
    sum_ti = float(sum(ti))
    t_seq = pair_count * sum_ti
    initiation = max(max(ti), launch_gap)
    t_pipe = sum_ti + (pair_count - 1) * initiation
    if t_pipe <= 0:
        return t_seq, t_pipe, 0.0, 0.0
    speedup = t_seq / t_pipe
    efficiency = speedup / n_stages if n_stages else 0.0
    return t_seq, t_pipe, speedup, efficiency


# ---------------------------------------------------------------------------
# Парсинг ti
# ---------------------------------------------------------------------------


def parse_ti_line(raw: str, n: int) -> List[int]:
    s = raw.strip()
    if not s:
        return [1] * n
    parts = [x.strip() for x in s.split(",") if x.strip()]
    if len(parts) == 1:
        v = int(parts[0])
        if v < 1:
            raise ValueError("каждый ti должен быть >= 1")
        return [v] * n
    if len(parts) != n:
        raise ValueError(f"нужно одно число или ровно {n} значений ti через запятую")
    out = [int(x) for x in parts]
    if any(x < 1 for x in out):
        raise ValueError("каждый ti должен быть >= 1")
    return out


# ---------------------------------------------------------------------------
# Графики + .dat (для отчёта)
# ---------------------------------------------------------------------------


def _write_dat(path: str, xs: Sequence[float], theory_y: Sequence[float], actual_y: Sequence[float], title: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n")
        f.write("# x\ttheory\tactual\n")
        for x, yt, ya in zip(xs, theory_y, actual_y):
            f.write(f"{x}\t{yt:.6f}\t{ya:.6f}\n")


def export_curves(
    n_fixed: int,
    r_fixed: int,
    pair_count: int,
    p: int,
    max_n: int,
    max_r: int,
    base_dir: str,
) -> Optional[str]:
    """
    Семейства S(n), E(n) при фиксированном r и S(r), E(r) при фиксированном n.
    Один и тот же набор пар для всех точек внутри каждого семейства (сравнение корректно).
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        print("matplotlib не установлен — графики и .dat пропущены (pip install matplotlib).")
        return None

    mx = (1 << p) - 1
    rng = random.Random(2026)

    # --- S(n), E(n) при фиксированном r: одна матрица пар на все n ---
    xs_n = list(range(1, max_n + 1))
    queue_n = [(rng.randint(1, mx), rng.randint(1, mx)) for _ in range(pair_count)]
    s_t_n, s_a_n, e_t_n, e_a_n = [], [], [], []
    for n in xs_n:
        ti = (1,) * n
        t_seq, _, st, et = theoretical_metrics(n, pair_count, r_fixed, ti)
        T, _ = simulate(queue_n, ti, p, n, r_fixed, visualize=False)
        sf = t_seq / T if T else 0.0
        s_t_n.append(st)
        s_a_n.append(sf)
        e_t_n.append(et)
        e_a_n.append(sf / n if n else 0.0)

    # --- S(r), E(r) при фиксированном n: те же пары на все r ---
    xs_r = list(range(1, max_r + 1))
    queue_r = [(rng.randint(1, mx), rng.randint(1, mx)) for _ in range(pair_count)]
    s_t_r, s_a_r, e_t_r, e_a_r = [], [], [], []
    for rv in xs_r:
        ti = (1,) * n_fixed
        t_seq, _, st, et = theoretical_metrics(n_fixed, pair_count, rv, ti)
        T, _ = simulate(queue_r, ti, p, n_fixed, rv, visualize=False)
        sf = t_seq / T if T else 0.0
        s_t_r.append(st)
        s_a_r.append(sf)
        e_t_r.append(et)
        e_a_r.append(sf / n_fixed if n_fixed else 0.0)

    _write_dat(
        os.path.join(base_dir, f"{DAT_PREFIX}_Sn_r{r_fixed}.dat"),
        [float(x) for x in xs_n],
        s_t_n,
        s_a_n,
        f"S(n), r={r_fixed}",
    )
    _write_dat(
        os.path.join(base_dir, f"{DAT_PREFIX}_En_r{r_fixed}.dat"),
        [float(x) for x in xs_n],
        e_t_n,
        e_a_n,
        f"E(n), r={r_fixed}",
    )
    _write_dat(
        os.path.join(base_dir, f"{DAT_PREFIX}_Sr_n{n_fixed}.dat"),
        [float(x) for x in xs_r],
        s_t_r,
        s_a_r,
        f"S(r), n={n_fixed}",
    )
    _write_dat(
        os.path.join(base_dir, f"{DAT_PREFIX}_Er_n{n_fixed}.dat"),
        [float(x) for x in xs_r],
        e_t_r,
        e_a_r,
        f"E(r), n={n_fixed}",
    )

    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.2))
    fig.suptitle("ЛР1, вар. 15: ускорение и эффективность")

    axes[0, 0].plot(xs_n, s_t_n, label="теория")
    axes[0, 0].plot(xs_n, s_a_n, label="факт")
    axes[0, 0].set_title(f"S(n) при r = {r_fixed}")
    axes[0, 0].set_xlabel("n")
    axes[0, 0].grid(True, alpha=0.28)
    axes[0, 0].legend()

    axes[0, 1].plot(xs_n, e_t_n, label="теория")
    axes[0, 1].plot(xs_n, e_a_n, label="факт")
    axes[0, 1].set_title(f"E(n) при r = {r_fixed}")
    axes[0, 1].set_xlabel("n")
    axes[0, 1].grid(True, alpha=0.28)
    axes[0, 1].legend()

    axes[1, 0].plot(xs_r, s_t_r, label="теория")
    axes[1, 0].plot(xs_r, s_a_r, label="факт")
    axes[1, 0].set_title(f"S(r) при n = {n_fixed}")
    axes[1, 0].set_xlabel("r")
    axes[1, 0].grid(True, alpha=0.28)
    axes[1, 0].legend()

    axes[1, 1].plot(xs_r, e_t_r, label="теория")
    axes[1, 1].plot(xs_r, e_a_r, label="факт")
    axes[1, 1].set_title(f"E(r) при n = {n_fixed}")
    axes[1, 1].set_xlabel("r")
    axes[1, 1].grid(True, alpha=0.28)
    axes[1, 1].legend()

    fig.tight_layout()
    png_path = os.path.join(base_dir, GRAPH_FILENAME)
    fig.savefig(png_path, dpi=GRAPH_DPI)
    print(f"PNG: {png_path}")
    print(f"DAT: {DAT_PREFIX}_*.dat в каталоге {base_dir}")
    return png_path


# ---------------------------------------------------------------------------
# Ввод
# ---------------------------------------------------------------------------


def _read_pairs_manual(m: int, p: int) -> List[Tuple[int, int]]:
    mx = (1 << p) - 1
    out: List[Tuple[int, int]] = []
    while len(out) < m:
        try:
            a = int(input("множимое A: ").strip())
            b = int(input("множитель B: ").strip())
        except ValueError:
            print("нужны целые числа")
            continue
        if not (1 <= a <= mx and 1 <= b <= mx):
            print(f"диапазон операндов: 1 .. {mx}")
            continue
        out.append((a, b))
        if len(out) < m:
            if input("ещё пара? (пусто — да, 1 — остановиться и добить случайно): ").strip() == "1":
                rng = random.Random()
                while len(out) < m:
                    out.append((rng.randint(1, mx), rng.randint(1, mx)))
                break
    return out


def _read_pairs_random(m: int, p: int, seed: Optional[int]) -> List[Tuple[int, int]]:
    rng = random.Random(seed)
    mx = (1 << p) - 1
    return [(rng.randint(1, mx), rng.randint(1, mx)) for _ in range(m)]


def print_input_preview(queue: Sequence[Tuple[int, int]], k: int = 3) -> None:
    """П. методички: до конвейера не менее трёх пар в десятичном виде с индексами."""
    print("\nВход (первые пары векторов A, B):")
    print(f"{'idx':>4} | {'A':>6} | {'B':>6}")
    for i in range(min(k, len(queue))):
        a, b = queue[i]
        print(f"{i:4d} | {a:6d} | {b:6d}")
    print()


def print_output_table(results: Sequence[dict], k: int = 3) -> None:
    """П. методички: не менее трёх компонент C с индексом и тактом."""
    rows = sorted(results, key=lambda r: r["i"])
    print("Вектор C (десятичн., индекс, такт готовности):")
    print(f"{'idx':>4} | {'A':>6} | {'B':>6} | {'C':>8} | {'t':>4}")
    for row in rows[:k]:
        print(f"{row['i']:4d} | {row['a']:6d} | {row['b']:6d} | {row['c']:8d} | {row['t']:4d}")
    if len(rows) > 2 * k:
        print("  ...")
        for row in rows[-k:]:
            print(f"{row['i']:4d} | {row['a']:6d} | {row['b']:6d} | {row['c']:8d} | {row['t']:4d}")
    elif len(rows) > k:
        for row in rows[k:]:
            print(f"{row['i']:4d} | {row['a']:6d} | {row['b']:6d} | {row['c']:8d} | {row['t']:4d}")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _demo() -> None:
    queue = [(3, 5), (11, 9), (200, 17)]
    ti = [1] * 8
    T, out = simulate(queue, ti, p=8, n_stages=8, launch_gap=1, visualize=False)
    err = verify(queue, out)
    print("demo:", "тактов", T, "ошибок проверки", len(err))
    print_input_preview(queue, 3)
    print_output_table(out, 3)


def _help() -> None:
    print("Запуск: python main.py")
    print("        python main.py --demo   (автопроверка без вопросов)")
    print("        python main.py --help")


def main() -> None:
    if len(sys.argv) > 1:
        if sys.argv[1] in ("-h", "--help"):
            _help()
            return
        if sys.argv[1] == "--demo":
            _demo()
            return

    print("ЛР1, вариант 15 — конвейерное умножение\n")

    try:
        n = int(input("число этапов n [8]: ").strip() or "8")
        r = int(input("интервал запуска r [1]: ").strip() or "1")
        m = int(input("число пар m (>=3) [8]: ").strip() or "8")
        p = int(input("разрядность p [8]: ").strip() or "8")
        ti = parse_ti_line(
            input(f"ti: пусто = единицы; одно число на все; или {n} через запятую: "),
            n,
        )
    except ValueError as e:
        print("Ошибка ввода:", e)
        return

    if n < 1 or r < 1 or p < 1:
        print("n, r, p должны быть >= 1")
        return
    if m < 3:
        m = 3
        print("m поднят до 3 (требование методички).")

    mode = (input("пары: 1 — вручную, иначе — случайно: ").strip() or "2").lower()
    seed_in = input("seed для случайных (пусто — системный): ").strip()
    seed = int(seed_in) if seed_in else None

    if mode == "1":
        queue = _read_pairs_manual(m, p)
    else:
        queue = _read_pairs_random(m, p, seed)

    step = (input("пошаговая отрисовка каждого такта? (y/N): ").strip().lower() or "n").startswith("y")

    print_input_preview(queue, 3)
    if step:
        T, results = simulate(queue, ti, p, n, r, visualize=True)
    else:
        print("Счёт без пошаговой отрисовки…")
        T, results = simulate(queue, ti, p, n, r, visualize=False)

    print("\n" + " ИТОГ ".center(CONSOLE_WIDTH, "="))
    print_output_table(results, 3)

    err = verify(queue, results)
    if err:
        print("ОШИБКА проверки A*B:", err[:5])
    else:
        print("Проверка A*B: OK.")

    t_seq, t_pipe, s_th, e_th = theoretical_metrics(n, m, r, ti)
    s_ac = t_seq / T if T else 0.0
    e_ac = s_ac / n if n else 0.0
    print("Время (условные такты):")
    print(f"  Tпослед  (теор.) ≈ {t_seq:.3f}")
    print(f"  Tконвейер(теор.) ≈ {t_pipe:.3f}")
    print(f"  фактически тактов: {T}")
    print(f"  S (теор.) ≈ {s_th:.4f}   E (теор.) ≈ {e_th:.4f}")
    print(f"  S (факт.) ≈ {s_ac:.4f}   E (факт.) ≈ {e_ac:.4f}")

    if (input("\nСохранить графики S/E и .dat? (y/N): ").strip().lower() or "n").startswith("y"):
        mxn = int(input("макс. n для графика [14]: ").strip() or "14")
        mxr = int(input("макс. r для графика [8]: ").strip() or "8")
        base = os.path.dirname(os.path.abspath(__file__))
        export_curves(n, r, m, p, mxn, mxr, base)


if __name__ == "__main__":
    main()
