#!/usr/bin/env python3

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError as exc:
    print(
        f"error: a required plotting dependency is missing ({exc.name}). "
        f"Install it with: pip install matplotlib numpy",
        file=sys.stderr,
    )
    raise SystemExit(1)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Strategy coverage heatmap (rows = strategies, cols = goals).",
        epilog=(
            "example:\n"
            "  ./portfolioStrategies.py merged.json plots/\n\n"
            "The input JSON is the output of evaluateMirabelleLog.sh (a list of "
            "log entries); one heatmap PNG is written per SMT solver."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input_json", help="Path to merged JSON")
    parser.add_argument("output_dir", help="Directory for output PNGs")
    parser.add_argument(
        "--max-width",
        type=float,
        default=40.0,
        help=(
            "Maximum figure width in inches (default: 40). With many goals the "
            "per-cell width shrinks to fit instead of producing an enormous figure."
        ),
    )
    args = parser.parse_args()

    if args.max_width <= 0:
        print(
            f"error: --max-width must be positive, got {args.max_width}",
            file=sys.stderr,
        )
        return 1

    input_path = Path(args.input_json)
    if not input_path.exists():
        print(f"error: input JSON does not exist: {input_path}", file=sys.stderr)
        return 1
    if not input_path.is_file():
        print(
            f"error: input JSON is not a regular file (is it a directory?): "
            f"{input_path}",
            file=sys.stderr,
        )
        return 1

    try:
        raw_text = input_path.read_text()
    except OSError as exc:
        print(f"error: could not read {input_path}: {exc}", file=sys.stderr)
        return 1

    try:
        entries = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        print(
            f"error: {input_path} is not valid JSON: {exc}",
            file=sys.stderr,
        )
        return 1

    if not isinstance(entries, list):
        print(
            f"error: expected {input_path} to contain a JSON list of log entries, "
            f"but got {type(entries).__name__}.",
            file=sys.stderr,
        )
        return 1

    if not entries:
        print(
            f"warning: {input_path} contains no entries; no plots will be written.",
            file=sys.stderr,
        )

    solved: dict[str, dict[str, set]] = collections.defaultdict(
        lambda: collections.defaultdict(set)
    )
    all_goals: set = set()

    def record(solver, strategy, outcome, bench):
        if solver is None or bench is None:
            return
        if outcome and outcome.startswith("success"):
            solved[solver][strategy or "best"].add(bench)

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            print(
                f"warning: skipping entry {index}: expected an object, "
                f"got {type(entry).__name__}.",
                file=sys.stderr,
            )
            continue
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
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(
            f"error: could not create output directory {output_dir}: {exc}",
            file=sys.stderr,
        )
        return 1

    plots_written = 0
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

        # Width grows with the number of goals, but is capped so that a large
        # benchmark does not produce an unviewably wide figure. Because imshow
        # uses aspect="auto", capping the width simply shrinks each cell to fit.
        width = min(args.max_width, max(14.0, 0.25 * len(goals) + 5.0))
        fig, ax = plt.subplots(
            figsize=(
                width,
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
        try:
            fig.savefig(out_path, dpi=150)
        except OSError as exc:
            print(f"error: could not write {out_path}: {exc}", file=sys.stderr)
            plt.close(fig)
            return 1
        plt.close(fig)
        plots_written += 1
        print(f"wrote {out_path}")

    if plots_written == 0:
        print(
            f"warning: no plots were written (no solver had any solved goals in "
            f"{input_path}).",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
