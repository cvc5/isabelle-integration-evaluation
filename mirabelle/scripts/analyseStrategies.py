#!/usr/bin/env python3

from __future__ import annotations

import argparse
import collections
import json
import statistics
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Plot preplay times per strategy, one horizontal bar chart per solver."
    )
    parser.add_argument("input_json", help="Path to merged JSON (entries with 'calls')")
    parser.add_argument(
        "output_dir",
        help="Directory to write one PNG per solver (e.g. preplay_cvc5.png)",
    )
    parser.add_argument(
        "--aggregate",
        choices=("mean", "median"),
        default="mean",
        help="How to combine preplay_time across entries (default: mean)",
    )
    args = parser.parse_args()

    entries = json.loads(Path(args.input_json).read_text())

    all_goals: set = set()
    for entry in entries:
        bench = (entry.get("session"), entry.get("theory"), entry.get("base"))
        if any(p is None for p in bench):
            continue
        if entry.get("outcome"):
            all_goals.add(bench)
    n_goals = len(all_goals)

    metrics = {
        "preplay_time": {
            "prefix": "preplay",
            "xlabel": "preplay time (ms",
            "title": "preplay time",
        },
        "proof_size": {
            "prefix": "proofsize",
            "xlabel": "proof size (lines",
            "title": "proof size",
        },
    }
    data: dict[str, dict[str, dict[str, list[float]]]] = {
        field: collections.defaultdict(lambda: collections.defaultdict(list))
        for field in metrics
    }
    attempted: dict[str, dict[str, set]] = collections.defaultdict(
        lambda: collections.defaultdict(set)
    )
    solved: dict[str, dict[str, set]] = collections.defaultdict(
        lambda: collections.defaultdict(set)
    )

    def record(solver, strategy, outcome, numeric, benchmark_id):
        if solver is None:
            return
        key = strategy or "best"
        for field in metrics:
            value = numeric.get(field)
            if isinstance(value, (int, float)):
                data[field][solver][key].append(float(value))
        if outcome is not None and benchmark_id is not None:
            attempted[solver][key].add(benchmark_id)
            if outcome.startswith("success"):
                solved[solver][key].add(benchmark_id)

    for entry in entries:
        bench = (entry.get("session"), entry.get("theory"), entry.get("base"))
        if any(part is None for part in bench):
            bench = None
        record(
            entry.get("suggested_backend"),
            entry.get("strategy"),
            entry.get("outcome"),
            entry,
            bench,
        )
        for call in entry.get("calls") or []:
            record(
                call.get("solver"),
                call.get("strategy"),
                call.get("outcome"),
                call,
                bench,
            )

    combine = statistics.mean if args.aggregate == "mean" else statistics.median

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    wrote_any = False
    for field, meta in metrics.items():
        per_solver = data[field]
        if not per_solver:
            print(f"No {field} values found; skipping.")
            continue
        for solver in sorted(per_solver):
            by_strategy = per_solver[solver]
            pairs = sorted(
                ((strategy, combine(vals)) for strategy, vals in by_strategy.items()),
                key=lambda p: p[1],
            )
            strategies = [p[0] for p in pairs]
            values = [p[1] for p in pairs]

            fig, ax = plt.subplots(figsize=(8, max(2.5, 0.4 * len(strategies) + 1.5)))
            ax.barh(strategies, values, color="steelblue")
            ax.set_xlabel(
                f"{meta['xlabel']}, {args.aggregate} over {n_goals} goals)"
            )
            ax.set_ylabel("strategy")
            ax.set_title(f"{solver}: {meta['title']} by strategy")
            for i, v in enumerate(values):
                ax.text(v, i, f" {v:.0f}", va="center")
            fig.tight_layout()

            out_path = output_dir / f"{meta['prefix']}_{solver}.png"
            fig.savefig(out_path, dpi=150)
            plt.close(fig)
            print(f"wrote {out_path} ({len(strategies)} strategies)")
            wrote_any = True

    if not attempted:
        print("No calls found; skipping success plots.")
    for solver in sorted(attempted):
        by_strategy = attempted[solver]
        solved_by_strategy = solved.get(solver, {})
        pairs = sorted(
            (
                (strategy, len(solved_by_strategy.get(strategy, set())), len(benches))
                for strategy, benches in by_strategy.items()
            ),
            key=lambda p: p[1],
        )
        strategies = [p[0] for p in pairs]
        successes = [p[1] for p in pairs]
        totals = [p[2] for p in pairs]
        uniques = []
        for strategy in strategies:
            mine = solved_by_strategy.get(strategy, set())
            others = set()
            for other, bms in solved_by_strategy.items():
                if other != strategy:
                    others |= bms
            uniques.append(len(mine - others))

        fig, ax = plt.subplots(figsize=(8, max(2.5, 0.4 * len(strategies) + 1.5)))
        bars = ax.barh(strategies, successes, color="seagreen")
        bar_height = bars[0].get_height() if bars else 0.8
        for i, u in enumerate(uniques):
            ax.vlines(
                u, i - bar_height / 2, i + bar_height / 2,
                colors="black", linewidth=2,
            )
        ax.set_xlabel("goals solved (black tick: unique solves for this solver)")
        ax.set_ylabel("strategy")
        ax.set_title(f"{solver}: goals solved by strategy (of {n_goals} goals)")
        for i, (s, t, u) in enumerate(zip(successes, totals, uniques)):
            rate = s / t if t else 0.0
            ax.text(s, i, f" {s}/{t} ({rate:.0%}), {u} unique", va="center")
        fig.tight_layout()

        out_path = output_dir / f"success_{solver}.png"
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        print(f"wrote {out_path} ({len(strategies)} strategies)")
        wrote_any = True

    if not wrote_any:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
