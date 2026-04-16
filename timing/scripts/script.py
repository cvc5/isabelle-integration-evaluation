#!/usr/bin/env python3
"""Build one by-rule CSV and three by-rule plots from a txt file or directory.

Usage:
    python3 script.py <file_or_folder> <output_folder>

The input can be:
- one stats txt file
- one directory containing nested txt spy files

The output folder will contain:
- by-rule.csv
- by-rules-total-barplot.png
- by-rules-mean-barplot.png
- by-rules-boxplot.png
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas

from txt_to_by_rule_csv import aggregate_samples, discover_input_files, merge_samples, write_csv


DPI = 200
NUM_RULES_PLOTS = 25


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert one txt file or a directory of nested txt files into by-rule.csv "
            "and three plots in the given output folder."
        )
    )
    parser.add_argument("input_path", help="Input txt file or directory.")
    parser.add_argument("output_dir", help="Output folder.")
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


def build_total_bar_plot(input_csv: Path, output_image: Path) -> None:
    plt = import_plotting()
    by_rule = read_by_rule_csv(input_csv)
    by_rule = by_rule.nlargest(NUM_RULES_PLOTS, "total").sort_values(by="total")

    fig, ax = plt.subplots()
    ax.barh(by_rule["rule"], by_rule["total"], color="#555555")
    ax.set_xlabel("total time (s)")
    fig.tight_layout()
    fig.savefig(output_image, dpi=DPI)
    plt.close(fig)


def build_mean_bar_plot(input_csv: Path, output_image: Path) -> None:
    plt = import_plotting()
    by_rule = read_by_rule_csv(input_csv)
    by_rule = by_rule.nlargest(NUM_RULES_PLOTS, "mean").sort_values(by="mean")

    fig, ax = plt.subplots()
    ax.barh(by_rule["rule"], by_rule["mean"], color="#2d6a8a")
    ax.set_xlabel("mean time per occurrence (s)")
    fig.tight_layout()
    fig.savefig(output_image, dpi=DPI)
    plt.close(fig)


def build_box_plot(input_csv: Path, output_image: Path) -> None:
    plt = import_plotting()
    by_rule = read_by_rule_csv(input_csv)
    by_rule = by_rule.nlargest(NUM_RULES_PLOTS, "total").sort_values(by="total")

    fig, ax = plt.subplots()
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
    ax.set_xlabel("time (s)")
    fig.tight_layout()
    fig.savefig(output_image, dpi=DPI)
    plt.close(fig)


def run_pipeline(input_path: Path, output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    mpl_config_dir = output_dir / ".matplotlib"
    mpl_config_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config_dir))

    files = discover_input_files(input_path)
    samples, used_files = merge_samples(files)
    if not samples:
        raise SystemExit("error: no timing samples found in input")

    csv_path = output_dir / "by-rule.csv"
    total_bar_path = output_dir / "by-rules-total-barplot.png"
    mean_bar_path = output_dir / "by-rules-mean-barplot.png"
    boxplot_path = output_dir / "by-rules-boxplot.png"

    rows = aggregate_samples(samples)
    write_csv(rows, csv_path)

    build_total_bar_plot(csv_path, total_bar_path)
    build_mean_bar_plot(csv_path, mean_bar_path)
    build_box_plot(csv_path, boxplot_path)

    print(f"wrote {len(rows)} rule rows from {len(used_files)} txt file(s) to {csv_path}")
    print(f"wrote {total_bar_path}")
    print(f"wrote {mean_bar_path}")
    print(f"wrote {boxplot_path}")
    return 0


def main() -> int:
    args = parse_args()
    return run_pipeline(Path(args.input_path), Path(args.output_dir))


if __name__ == "__main__":
    raise SystemExit(main())
