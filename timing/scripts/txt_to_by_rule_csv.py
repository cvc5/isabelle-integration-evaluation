#!/usr/bin/env python3
"""Convert one stats txt file or a directory of stats txt files into by-rule CSV.

The generated CSV matches the schema expected by script.py:

    rule,count,total,mean,min,first_quartile,median,third_quartile,max

Input files are expected to contain one metadata header line followed by lines like:

    bind: 632000,613000,819000,
    resolution: 903000,1275000,2062000,

All timing values are kept in nanoseconds in the CSV.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import pandas


CSV_COLUMNS = [
    "rule",
    "count",
    "total",
    "mean",
    "min",
    "first_quartile",
    "median",
    "third_quartile",
    "max",
]

RULE_ALIASES = {
    "th_resolution": "resolution",
    "anchor(subproof)": "subproof",
    "anchor(onepoint)": "onepoint",
    "anchor(sko_ex)": "sko_ex",
    "anchor(sko_forall)": "sko_forall",
    "anchor(bind)": "bind",
    "anchor(let)": "let",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert one stats txt file or a directory of nested txt files into "
            "an aggregated by-rule CSV."
        )
    )
    parser.add_argument(
        "input_path",
        type=Path,
        help="Input txt file or directory containing nested txt files.",
    )
    parser.add_argument(
        "output_csv",
        type=Path,
        help="Output CSV path.",
    )
    return parser.parse_args()


def discover_input_files(input_path: Path) -> list[Path]:
    if not input_path.exists():
        raise FileNotFoundError(f"input path does not exist: {input_path}")

    if input_path.is_file():
        return [input_path]

    if input_path.is_dir():
        files = sorted(path for path in input_path.rglob("*.txt") if path.is_file())
        if files:
            return files
        raise FileNotFoundError(f"no .txt files found under directory: {input_path}")

    raise FileNotFoundError(f"unsupported input path: {input_path}")


def normalize_rule_name(rule: str) -> str:
    return RULE_ALIASES.get(rule, rule)


def is_metadata_line(line: str) -> bool:
    colon_index = line.find(":")
    semicolon_index = line.find(";")
    return colon_index != -1 and semicolon_index != -1 and semicolon_index < colon_index


def parse_stats_file(path: Path) -> dict[str, list[int]]:
    samples: dict[str, list[int]] = defaultdict(list)

    with path.open(encoding="utf-8", errors="replace") as handle:
        for lineno, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line or is_metadata_line(line):
                continue

            if ":" not in line:
                continue

            rule, values_text = line.split(":", 1)
            rule = normalize_rule_name(rule.strip())
            if not rule:
                continue

            values: list[int] = []
            for entry in values_text.split(","):
                entry = entry.strip()
                if not entry:
                    continue
                try:
                    values.append(int(entry))
                except ValueError as exc:
                    raise ValueError(
                        f"invalid timing value in {path}:{lineno}: {entry!r}"
                    ) from exc

            if values:
                samples[rule].extend(values)

    return samples


def merge_samples(files: list[Path]) -> tuple[dict[str, list[int]], list[Path]]:
    merged: dict[str, list[int]] = defaultdict(list)
    used_files: list[Path] = []

    for path in files:
        parsed = parse_stats_file(path)
        if not parsed:
            print(f"warning: no timing rows found in {path}, skipping", file=sys.stderr)
            continue

        used_files.append(path)
        for rule, values in parsed.items():
            merged[rule].extend(values)

    return merged, used_files


def maybe_int(value: float | int) -> float | int:
    if isinstance(value, int):
        return value
    if float(value).is_integer():
        return int(value)
    return value


def winsorize_series(
    series: pandas.Series,
    lower_quantile: float,
    upper_quantile: float,
) -> pandas.Series:
    series = series.astype("float64")
    lower_bound = series.quantile(lower_quantile, interpolation="linear")
    upper_bound = series.quantile(upper_quantile, interpolation="linear")
    return series.clip(lower=lower_bound, upper=upper_bound)


def aggregate_samples(
    samples: dict[str, list[int]],
    winsorize_limits: tuple[float, float] | None = None,
) -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []

    for rule, values in samples.items():
        series = pandas.Series(values, dtype="int64")
        summarized = series
        if winsorize_limits is not None:
            lower_quantile, upper_quantile = winsorize_limits
            summarized = winsorize_series(series, lower_quantile, upper_quantile)

        count = int(summarized.count())
        row = {
            "rule": rule,
            "count": count,
            "total": maybe_int(summarized.sum()),
            "mean": maybe_int(summarized.mean()),
            "min": maybe_int(summarized.min()),
            "first_quartile": maybe_int(summarized.quantile(0.25, interpolation="linear")),
            "median": maybe_int(summarized.quantile(0.50, interpolation="linear")),
            "third_quartile": maybe_int(summarized.quantile(0.75, interpolation="linear")),
            "max": maybe_int(summarized.max()),
        }
        rows.append(row)

    rows.sort(key=lambda row: (-int(row["total"]), str(row["rule"])))
    return rows


def write_csv(rows: list[dict[str, float | int | str]], output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    files = discover_input_files(args.input_path)
    samples, used_files = merge_samples(files)

    if not samples:
        print("error: no timing samples found in input", file=sys.stderr)
        return 1

    rows = aggregate_samples(samples)
    write_csv(rows, args.output_csv)

    print(
        f"wrote {len(rows)} rule rows from {len(used_files)} txt file(s) to {args.output_csv}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
