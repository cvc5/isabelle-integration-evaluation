#!/usr/bin/env python3

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Strategy coverage heatmap (rows = strategies, cols = goals)."
    )
    parser.add_argument("input_json", help="Path to merged JSON")
    parser.add_argument("output_dir", help="Directory for output PNGs")
    args = parser.parse_args()

    entries = json.loads(Path(args.input_json).read_text())

    solved: dict[str, dict[str, set]] = collections.defaultdict(
        lambda: collections.defaultdict(set)
    )
    all_goals: set = set()

    def record(solver, strategy, outcome, bench):
        if solver is None or bench is None:
            return
        if outcome and outcome.startswith("success"):
            solved[solver][strategy or "best"].add(bench)

    for entry in entries:
        bench = (entry.get("session"), entry.get("theory"), entry.get("base"))
        if any(p is None for p in bench):
            bench = None
        if bench is not None and entry.get("outcome"):
            all_goals.add(bench)
        record(
            entry.get("suggested_backend"),
            entry.get("strategy"),
            entry.get("outcome"),
            bench,
        )
        for call in entry.get("calls") or []:
            record(
                call.get("solver"),
                call.get("strategy"),
                call.get("outcome"),
                bench,
            )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for solver in sorted(solved):
        by_strategy = {s: set(b) for s, b in solved[solver].items() if b}
        if not by_strategy:
            continue

        names = sorted(by_strategy, key=lambda s: (-len(by_strategy[s]), s))

        uniques: dict[str, int] = {}
        for s in names:
            others = set().union(*(b for k, b in by_strategy.items() if k != s))
            uniques[s] = len(by_strategy[s] - others)

        goal_count: collections.Counter = collections.Counter()
        for bms in by_strategy.values():
            for b in bms:
                goal_count[b] += 1

        def signature(b):
            return tuple(b in by_strategy[n] for n in names)

        goals = sorted(goal_count, key=lambda b: (-goal_count[b], signature(b), b))
        goal_index = {b: i for i, b in enumerate(goals)}

        matrix = np.zeros((len(names), len(goals)), dtype=float)
        for r, name in enumerate(names):
            for b in by_strategy[name]:
                matrix[r, goal_index[b]] = 1.0

        fig, ax = plt.subplots(
            figsize=(
                max(14.0, 0.25 * len(goals) + 5.0),
                max(3.0, 0.3 * len(names) + 1.5),
            )
        )
        ax.imshow(matrix, aspect="auto", cmap="Greens", interpolation="nearest")
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(
            [f"{n} ({len(by_strategy[n])} solved, {uniques[n]} unique)" for n in names],
            fontsize=8,
        )
        n_goals = len(goals)
        step = max(1, 10 ** int(np.floor(np.log10(max(n_goals, 1)))) // 2 or 5)
        if n_goals <= 20:
            step = max(1, n_goals // 5)
        xticks = list(range(0, n_goals, step))
        if (n_goals - 1) not in xticks:
            xticks.append(n_goals - 1)
        ax.set_xticks(xticks)
        ax.set_xticklabels([str(t + 1) for t in xticks], fontsize=8)
        ax.set_xlabel(
            f"goal index ({n_goals} of {len(all_goals)} goals solved by some strategy)"
        )
        ax.set_title(f"{solver}: coverage heatmap")
        fig.tight_layout()
        out_path = output_dir / f"portfolio_heatmap_{solver}.png"
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        print(f"wrote {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
