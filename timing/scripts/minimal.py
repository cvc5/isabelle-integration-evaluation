#!/usr/bin/env python3
"""Build by-rule plots from an existing by-rule CSV."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from script import (
    build_box_plot,
    build_mean_bar_plot,
    build_scatter_plot,
    build_total_bar_plot,
    filter_label,
    parse_excluded_rules,
)


def filter_bounds_label(min_quantile: float | None, max_quantile: float | None) -> str:
    if min_quantile is None and max_quantile is None:
        return "csv"
    min_quantile = 0.0 if min_quantile is None else min_quantile
    max_quantile = 1.0 if max_quantile is None else max_quantile
    return f"csv {filter_label(min_quantile)}-{filter_label(max_quantile)}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path, help="Existing by-rule.csv file.")
    parser.add_argument("output_dir", type=Path, help="Output folder.")
    parser.add_argument("--max-rules", type=int, default=None)
    parser.add_argument("--min", dest="min_quantile", type=float, default=None)
    parser.add_argument("--max", dest="max_quantile", type=float, default=None)
    parser.add_argument("--exclude", default="", help="Comma-separated rules to skip.")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    mpl_config_dir = args.output_dir / ".matplotlib"
    mpl_config_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config_dir))

    excluded_rules = parse_excluded_rules(args.exclude)
    label = filter_bounds_label(args.min_quantile, args.max_quantile)
    build_total_bar_plot(args.input_csv, args.output_dir / "by-rules-total-barplot.png", args.max_rules, excluded_rules, label)
    build_mean_bar_plot(args.input_csv, args.output_dir / "by-rules-mean-barplot.png", args.max_rules, excluded_rules, label)
    build_box_plot(args.input_csv, args.output_dir / "by-rules-boxplot.png", args.max_rules, excluded_rules, label)
    build_scatter_plot(args.input_csv, args.output_dir / "by-rules-scatterplot.png", args.max_rules, excluded_rules)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
