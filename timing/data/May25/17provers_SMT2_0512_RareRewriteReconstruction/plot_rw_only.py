#!/usr/bin/env python3
"""Scatterplot of count vs mean from *-by-rule-p05-p95-rw-only.csv files in this folder.

Each file's points are drawn in a distinct color. Colors are hardcoded per
file index so the same number always gets the same color, regardless of which
subset is selected.

Use -i N (repeatable) to restrict to a subset, e.g. `-i 0 -i 4`.
"""

import argparse
import csv
import glob
import os
import sys

import matplotlib.pyplot as plt


# Hardcoded color per file index. Stable across runs and subsets.
COLORS = {
    0: "#1f77b4",  # blue
    1: "#ff7f0e",  # orange
    2: "#2ca02c",  # green
    3: "#d62728",  # red
    4: "#9467bd",  # purple
    5: "#8c564b",  # brown
    6: "#e377c2",  # pink
    7: "#7f7f7f",  # gray
    8: "#bcbd22",  # olive
    9: "#17becf",  # cyan
}

STRATEGIES = {
    0: "lemma, if fails simplify",
    1: "only lemma",
    2: "only simplify",
    3: "only simplify + lemmas in simpset",
    4: "lemmas for complex, simplify for easy",
    5: "lemmas for complex, simplify for easy + lemmas in simpset",
    6: "only match",
    7: "use lemma for complex, match for easy",
}


def file_index(path):
    return int(os.path.basename(path).split("-", 1)[0])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-i",
        dest="indices",
        type=int,
        action="append",
        help="Only include this file index (repeatable, e.g. -i 0 -i 4).",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the plot window in addition to saving.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output PNG path (default: rw_only_scatter[_<indices>].png).",
    )
    args = parser.parse_args()

    folder = os.path.dirname(os.path.abspath(__file__))
    pattern = os.path.join(folder, "*-by-rule-p05-p95-rw-only.csv")
    files = sorted(glob.glob(pattern), key=file_index)

    if not files:
        print(f"No files matching {pattern}", file=sys.stderr)
        sys.exit(1)

    if args.indices:
        wanted = set(args.indices)
        files = [p for p in files if file_index(p) in wanted]
        missing = wanted - {file_index(p) for p in files}
        if missing:
            print(
                f"Warning: no CSV found for index/indices {sorted(missing)}",
                file=sys.stderr,
            )
        if not files:
            print("No files left after filtering.", file=sys.stderr)
            sys.exit(1)

    fig, ax = plt.subplots(figsize=(10, 7))

    for path in files:
        idx = file_index(path)
        counts, means = [], []
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    counts.append(float(row["count"]))
                    means.append(float(row["mean"]))
                except (ValueError, KeyError):
                    continue
        label = f"{idx}: {STRATEGIES[idx]}" if idx in STRATEGIES else str(idx)
        ax.scatter(
            counts,
            means,
            color=COLORS.get(idx, "#000000"),
            label=label,
            alpha=0.6,
            edgecolors="none",
            s=25,
        )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("count")
    ax.set_ylabel("mean")
    ax.set_title("Rewrite rules: count vs mean (rw-only)")
    ax.legend(title="strategies", loc="best", fontsize=9)
    ax.grid(True, which="both", linestyle="--", alpha=0.3)

    if args.output:
        out = args.output
    elif args.indices:
        tag = "_".join(str(i) for i in sorted(set(args.indices)))
        out = os.path.join(folder, f"rw_only_scatter_{tag}.png")
    else:
        out = os.path.join(folder, "rw_only_scatter.png")

    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"Wrote {out}")

    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
