#!/usr/bin/env python3
# Originally written by Bruno Andreotti, UFMG.
# Modified by Tiago Campos, UFMG.
"""Build one by-rule CSV and by-rule plots from a txt file or directory.

Usage:
    python3 script.py <file_or_folder> <output_folder>

The input can be:
- one stats txt file
- one directory containing nested txt spy files

The output folder will contain:
- by-rule.csv
- by-rule-p05-p95.csv
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
DEFAULT_FILTER_LIMITS = (0.05, 0.95)


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
        default=None,
        help="Maximum number of rules to include across each plot family. Defaults to all rules.",
    )
    parser.add_argument(
        "--min",
        dest="min_quantile",
        type=float,
        default=DEFAULT_FILTER_LIMITS[0],
        help="Lower percentile filter bound in [0, 1]. Defaults to 0.05.",
    )
    parser.add_argument(
        "--max",
        dest="max_quantile",
        type=float,
        default=DEFAULT_FILTER_LIMITS[1],
        help="Upper percentile filter bound in [0, 1]. Defaults to 0.95.",
    )
    parser.add_argument(
        "--exclude",
        default="",
        help="Comma-separated rule names to exclude from plots.",
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


def parse_excluded_rules(exclude_arg: str) -> set[str]:
    return {rule.strip() for rule in exclude_arg.split(",") if rule.strip()}


def filter_label(value: float) -> str:
    percentage = value * 100.0
    if percentage.is_integer():
        return f"p{int(percentage)}"
    return f"p{str(round(percentage, 3)).rstrip('0').rstrip('.')}"


def filter_token(value: float) -> str:
    percentage = value * 100.0
    if percentage.is_integer():
        return f"p{int(percentage):02d}"
    return f"p{str(round(percentage, 3)).rstrip('0').rstrip('.').replace('.', '_')}"


def select_ranked_rules(
    input_csv: Path,
    metric: str,
    max_rules: int | None,
    excluded_rules: set[str],
) -> pandas.DataFrame:
    by_rule = read_by_rule_csv(input_csv)
    if excluded_rules:
        exact_rules = {rule for rule in excluded_rules if not rule.endswith("*")}
        prefix_rules = {rule[:-1] for rule in excluded_rules if rule.endswith("*")}
        by_rule = by_rule.loc[~by_rule["rule"].isin(exact_rules)].copy()
        if prefix_rules:
            by_rule = by_rule.loc[~by_rule["rule"].str.startswith(tuple(prefix_rules))].copy()

    if by_rule.empty:
        raise SystemExit("error: no rules remain after applying plotting filters")
    if max_rules is None:
        return by_rule.sort_values(by=metric, ascending=False).reset_index(drop=True)
    return by_rule.nlargest(max_rules, metric).reset_index(drop=True)


def plot_style(rule_count: int) -> tuple[float, float, float]:
    rule_count = max(rule_count, 1)
    figure_height = min(28.0, max(6.0, 0.24 * rule_count + 2.0))
    label_fontsize = min(10.0, max(4.0, 14.0 - 1.2 * math.log2(rule_count)))
    axis_fontsize = min(12.0, max(6.0, label_fontsize + 1.5))
    return figure_height, label_fontsize, axis_fontsize


def build_total_bar_plot(
    input_csv: Path,
    output_path: Path,
    max_rules: int | None,
    excluded_rules: set[str],
    filter_bounds_label: str,
) -> Path:
    plt = import_plotting()
    by_rule = select_ranked_rules(input_csv, "total", max_rules, excluded_rules)
    by_rule = by_rule.sort_values(by="total")
    figure_height, label_fontsize, axis_fontsize = plot_style(len(by_rule))

    fig, ax = plt.subplots(figsize=(12, figure_height))
    ax.barh(by_rule["rule"], by_rule["total"], color="#555555")
    ax.set_xlabel(f"{filter_bounds_label} filtered total time (s)", fontsize=axis_fontsize)
    ax.tick_params(axis="x", labelsize=max(6.0, label_fontsize))
    ax.tick_params(axis="y", labelsize=label_fontsize)
    fig.tight_layout()
    fig.savefig(output_path, dpi=DPI)
    plt.close(fig)
    return output_path


def build_mean_bar_plot(
    input_csv: Path,
    output_path: Path,
    max_rules: int | None,
    excluded_rules: set[str],
    filter_bounds_label: str,
) -> Path:
    plt = import_plotting()
    by_rule = select_ranked_rules(input_csv, "mean", max_rules, excluded_rules)
    by_rule = by_rule.sort_values(by="mean")
    figure_height, label_fontsize, axis_fontsize = plot_style(len(by_rule))

    fig, ax = plt.subplots(figsize=(12, figure_height))
    ax.barh(by_rule["rule"], by_rule["mean"], color="#2d6a8a")
    ax.set_xlabel(
        f"{filter_bounds_label} filtered mean time per occurrence (s)",
        fontsize=axis_fontsize,
    )
    ax.tick_params(axis="x", labelsize=max(6.0, label_fontsize))
    ax.tick_params(axis="y", labelsize=label_fontsize)
    fig.tight_layout()
    fig.savefig(output_path, dpi=DPI)
    plt.close(fig)
    return output_path


def build_box_plot(
    input_csv: Path,
    output_path: Path,
    max_rules: int | None,
    excluded_rules: set[str],
    filter_bounds_label: str,
) -> Path:
    plt = import_plotting()
    by_rule = select_ranked_rules(input_csv, "total", max_rules, excluded_rules)
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
    ax.set_xlabel(f"{filter_bounds_label} filtered time (s)", fontsize=axis_fontsize)
    ax.tick_params(axis="x", labelsize=max(6.0, label_fontsize))
    ax.tick_params(axis="y", labelsize=label_fontsize)
    fig.tight_layout()
    fig.savefig(output_path, dpi=DPI)
    plt.close(fig)
    return output_path


def build_scatter_plot(
    input_csv: Path,
    output_path: Path,
    max_rules: int | None,
    excluded_rules: set[str],
) -> Path:
    plt = import_plotting()
    by_rule = select_ranked_rules(input_csv, "mean", max_rules, excluded_rules)
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


def run_pipeline(
    input_path: Path,
    output_dir: Path,
    max_rules: int | None,
    min_quantile: float,
    max_quantile: float,
    excluded_rules: set[str],
) -> int:
    if not 0.0 <= min_quantile <= 1.0:
        raise SystemExit("error: --min must be between 0 and 1")
    if not 0.0 <= max_quantile <= 1.0:
        raise SystemExit("error: --max must be between 0 and 1")
    if min_quantile > max_quantile:
        raise SystemExit("error: --min must be less than or equal to --max")

    output_dir.mkdir(parents=True, exist_ok=True)
    mpl_config_dir = output_dir / ".matplotlib"
    mpl_config_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config_dir))

    files = discover_input_files(input_path)
    samples, used_files = merge_samples(files)
    if not samples:
        raise SystemExit("error: no timing samples found in input")

    csv_path = output_dir / "by-rule.csv"
    filter_bounds_label = f"{filter_label(min_quantile)}-{filter_label(max_quantile)}"
    filtered_csv_path = output_dir / f"by-rule-{filter_token(min_quantile)}-{filter_token(max_quantile)}.csv"
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
    filtered_rows = aggregate_samples(samples, trim_limits=(min_quantile, max_quantile))
    write_csv(rows, csv_path)
    write_csv(filtered_rows, filtered_csv_path)

    for stale_dir in stale_paged_outputs:
        if stale_dir.exists():
            shutil.rmtree(stale_dir)
    stale_csv_paths = [
        output_dir / "by-rule-central95.csv",
        output_dir / "by-rule-upper95.csv",
        output_dir / "by-rule-p05-p95.csv",
    ]
    for stale_csv_path in stale_csv_paths:
        if stale_csv_path != filtered_csv_path and stale_csv_path.exists():
            stale_csv_path.unlink()
    for stale_filtered_csv_path in output_dir.glob("by-rule-p*-p*.csv"):
        if stale_filtered_csv_path != filtered_csv_path and stale_filtered_csv_path.exists():
            stale_filtered_csv_path.unlink()

    build_total_bar_plot(filtered_csv_path, total_bar_path, max_rules, excluded_rules, filter_bounds_label)
    build_mean_bar_plot(filtered_csv_path, mean_bar_path, max_rules, excluded_rules, filter_bounds_label)
    build_box_plot(filtered_csv_path, boxplot_path, max_rules, excluded_rules, filter_bounds_label)
    build_scatter_plot(csv_path, scatterplot_path, max_rules, excluded_rules)

    print(f"wrote {len(rows)} rule rows from {len(used_files)} txt file(s) to {csv_path}")
    print(f"wrote {filter_bounds_label} filtered rule rows to {filtered_csv_path}")
    if excluded_rules:
        print(f"excluded {len(excluded_rules)} rule(s) from plots: {', '.join(sorted(excluded_rules))}")
    print(f"wrote total bar plot to {total_bar_path}")
    print(f"wrote mean bar plot to {mean_bar_path}")
    print(f"wrote box plot to {boxplot_path}")
    print(f"wrote scatter plot to {scatterplot_path}")
    return 0


def main() -> int:
    args = parse_args()
    return run_pipeline(
        Path(args.input_path),
        Path(args.output_dir),
        args.max_rules,
        args.min_quantile,
        args.max_quantile,
        parse_excluded_rules(args.exclude),
    )


if __name__ == "__main__":
    raise SystemExit(main())
