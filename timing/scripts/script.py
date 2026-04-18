#!/usr/bin/env python3
"""Build one by-rule CSV and by-rule plots from a txt file or directory.

Usage:
    python3 script.py <file_or_folder> <output_folder>

The input can be:
- one stats txt file
- one directory containing nested txt spy files

The output folder will contain:
- by-rule.csv
- by-rule-central95.csv
- by-rules-total-barplot.png
- by-rules-mean-barplot.png
- by-rules-boxplot.png
- by-rules-scatterplot.png
"""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
import shutil

import pandas

from txt_to_by_rule_csv import aggregate_samples, discover_input_files, merge_samples, write_csv


DPI = 200
DEFAULT_MAX_RULES = 25
CENTRAL_95_LIMITS = (0.025, 0.975)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert one txt file or a directory of nested txt files into by-rule.csv "
            "and plots in the given output folder."
        )
    )
    parser.add_argument("input_path", help="Input txt file or directory.")
    parser.add_argument("output_dir", help="Output folder.")
    parser.add_argument(
        "--max-rules",
        type=int,
        default=DEFAULT_MAX_RULES,
        help="Maximum number of rules to include across each plot family.",
    )
    return parser.parse_args()


def import_plotting():
    import matplotlib.pyplot as plt
    return plt


def combine_rules(df: pandas.DataFrame, rule_a: str, rule_b: str) -> pandas.DataFrame:
    rule_a_entries = df.loc[df["rule"] == rule_a][["total", "mean", "count"]]
    if len(rule_a_entries) == 0:
        return df
    df.loc[df["rule"] == rule_b, ["total", "mean", "count"]] += rule_a_entries.iloc[0]
    return df[df["rule"] != rule_a]


def convert_columns_to_seconds(df: pandas.DataFrame, columns_in_nanos: list[str]) -> None:
    columns_in_nanos = [column for column in columns_in_nanos if column in df.columns]
    df[columns_in_nanos] = df[columns_in_nanos].apply(lambda ns: ns / 1_000_000_000.0)


def read_by_rule_csv(filename: Path) -> pandas.DataFrame:
    df = pandas.read_csv(filename)
    convert_columns_to_seconds(
        df,
        ["total", "mean", "min", "first_quartile", "median", "third_quartile", "max"],
    )
    df = combine_rules(df, "th_resolution", "resolution")
    for rule in ["subproof", "onepoint", "sko_ex", "sko_forall", "bind", "let"]:
        df = combine_rules(df, f"anchor({rule})", rule)
    return df


def select_ranked_rules(input_csv: Path, metric: str, max_rules: int) -> pandas.DataFrame:
    by_rule = read_by_rule_csv(input_csv)
    return by_rule.nlargest(max_rules, metric).reset_index(drop=True)


def plot_style(rule_count: int) -> tuple[float, float, float]:
    rule_count = max(rule_count, 1)
    figure_height = min(28.0, max(6.0, 0.24 * rule_count + 2.0))
    label_fontsize = min(10.0, max(4.0, 14.0 - 1.2 * math.log2(rule_count)))
    axis_fontsize = min(12.0, max(6.0, label_fontsize + 1.5))
    return figure_height, label_fontsize, axis_fontsize


def build_total_bar_plot(input_csv: Path, output_path: Path, max_rules: int) -> Path:
    plt = import_plotting()
    by_rule = select_ranked_rules(input_csv, "total", max_rules)
    by_rule = by_rule.sort_values(by="total")
    figure_height, label_fontsize, axis_fontsize = plot_style(len(by_rule))

    fig, ax = plt.subplots(figsize=(12, figure_height))
    ax.barh(by_rule["rule"], by_rule["total"], color="#555555")
    ax.set_xlabel("winsorized total time (central 95%) (s)", fontsize=axis_fontsize)
    ax.tick_params(axis="x", labelsize=max(6.0, label_fontsize))
    ax.tick_params(axis="y", labelsize=label_fontsize)
    fig.tight_layout()
    fig.savefig(output_path, dpi=DPI)
    plt.close(fig)
    return output_path


def build_mean_bar_plot(input_csv: Path, output_path: Path, max_rules: int) -> Path:
    plt = import_plotting()
    by_rule = select_ranked_rules(input_csv, "mean", max_rules)
    by_rule = by_rule.sort_values(by="mean")
    figure_height, label_fontsize, axis_fontsize = plot_style(len(by_rule))

    fig, ax = plt.subplots(figsize=(12, figure_height))
    ax.barh(by_rule["rule"], by_rule["mean"], color="#2d6a8a")
    ax.set_xlabel("winsorized mean time per occurrence (central 95%) (s)", fontsize=axis_fontsize)
    ax.tick_params(axis="x", labelsize=max(6.0, label_fontsize))
    ax.tick_params(axis="y", labelsize=label_fontsize)
    fig.tight_layout()
    fig.savefig(output_path, dpi=DPI)
    plt.close(fig)
    return output_path


def build_box_plot(input_csv: Path, output_path: Path, max_rules: int) -> Path:
    plt = import_plotting()
    by_rule = select_ranked_rules(input_csv, "total", max_rules)
    by_rule = by_rule.sort_values(by="total")
    figure_height, label_fontsize, axis_fontsize = plot_style(len(by_rule))

    fig, ax = plt.subplots(figsize=(12, figure_height))
    boxplot = [
        {
            "label": row["rule"],
            "whislo": row["min"],
            "q1": row["first_quartile"],
            "med": row["median"],
            "q3": row["third_quartile"],
            "whishi": row["max"],
        }
        for _, row in by_rule.iterrows()
    ]
    ax.bxp(boxplot, shownotches=False, showmeans=False, showfliers=False, vert=False)
    ax.set_xlabel("winsorized time (central 95%) (s)", fontsize=axis_fontsize)
    ax.tick_params(axis="x", labelsize=max(6.0, label_fontsize))
    ax.tick_params(axis="y", labelsize=label_fontsize)
    fig.tight_layout()
    fig.savefig(output_path, dpi=DPI)
    plt.close(fig)
    return output_path


def build_scatter_plot(input_csv: Path, output_path: Path, max_rules: int) -> Path:
    plt = import_plotting()
    by_rule = select_ranked_rules(input_csv, "mean", max_rules)
    figure_height, label_fontsize, axis_fontsize = plot_style(len(by_rule))
    annotation_fontsize = max(3.5, label_fontsize - 1.0)

    fig, ax = plt.subplots(figsize=(14, max(8.0, figure_height)))
    ax.scatter(by_rule["count"], by_rule["mean"], color="#8a3b2d", s=28, alpha=0.85)
    ax.set_xlabel("occurrence count", fontsize=axis_fontsize)
    ax.set_ylabel("raw mean time per occurrence (s)", fontsize=axis_fontsize)
    ax.tick_params(axis="x", labelsize=max(6.0, label_fontsize))
    ax.tick_params(axis="y", labelsize=max(6.0, label_fontsize))

    if (by_rule["count"] > 0).all():
        ax.set_xscale("log")
    if (by_rule["mean"] > 0).all():
        ax.set_yscale("log")

    for _, row in by_rule.iterrows():
        ax.annotate(
            row["rule"],
            (row["count"], row["mean"]),
            xytext=(3, 3),
            textcoords="offset points",
            fontsize=annotation_fontsize,
        )

    fig.tight_layout()
    fig.savefig(output_path, dpi=DPI)
    plt.close(fig)
    return output_path


def run_pipeline(input_path: Path, output_dir: Path, max_rules: int) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    mpl_config_dir = output_dir / ".matplotlib"
    mpl_config_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config_dir))

    files = discover_input_files(input_path)
    samples, used_files = merge_samples(files)
    if not samples:
        raise SystemExit("error: no timing samples found in input")

    csv_path = output_dir / "by-rule.csv"
    central95_csv_path = output_dir / "by-rule-central95.csv"
    total_bar_path = output_dir / "by-rules-total-barplot.png"
    mean_bar_path = output_dir / "by-rules-mean-barplot.png"
    boxplot_path = output_dir / "by-rules-boxplot.png"
    scatterplot_path = output_dir / "by-rules-scatterplot.png"
    stale_paged_outputs = [
        output_dir / "total-barplots",
        output_dir / "mean-barplots",
        output_dir / "boxplots",
    ]

    rows = aggregate_samples(samples)
    central95_rows = aggregate_samples(samples, winsorize_limits=CENTRAL_95_LIMITS)
    write_csv(rows, csv_path)
    write_csv(central95_rows, central95_csv_path)

    for stale_dir in stale_paged_outputs:
        if stale_dir.exists():
            shutil.rmtree(stale_dir)

    build_total_bar_plot(central95_csv_path, total_bar_path, max_rules)
    build_mean_bar_plot(central95_csv_path, mean_bar_path, max_rules)
    build_box_plot(central95_csv_path, boxplot_path, max_rules)
    build_scatter_plot(csv_path, scatterplot_path, max_rules)

    print(f"wrote {len(rows)} rule rows from {len(used_files)} txt file(s) to {csv_path}")
    print(f"wrote winsorized central-95% rule rows to {central95_csv_path}")
    print(f"wrote total bar plot to {total_bar_path}")
    print(f"wrote mean bar plot to {mean_bar_path}")
    print(f"wrote box plot to {boxplot_path}")
    print(f"wrote scatter plot to {scatterplot_path}")
    return 0


def main() -> int:
    args = parse_args()
    return run_pipeline(Path(args.input_path), Path(args.output_dir), args.max_rules)


if __name__ == "__main__":
    raise SystemExit(main())
