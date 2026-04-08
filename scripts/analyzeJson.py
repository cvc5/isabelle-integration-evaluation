#!/usr/bin/env python3
"""Analyze benchmark results from JSON data.

Parses solver benchmark results, computes statistics (solve counts, line counts,
timing), and outputs summary tables or detailed per-library reports. Optionally
exports to CSV.
"""

import csv
import json
import os
import sys
import math
from argparse import ArgumentParser
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_user_time(solving_time: str) -> Optional[float]:
    """Extract user time from a /usr/bin/time-style string.

    Example input:
      '0.01user 0.00system 0:00.02elapsed 86%CPU ...'
    Returns:
      0.01
    """
    try:
        for part in solving_time.split():
            if part.endswith("user"):
                return float(part.replace("user", ""))
    except Exception:
        pass
    return None


# Mapping of checking_outcome codes to human-readable labels.
CHECKING_OUTCOMES: dict[int, str] = {
    0: "Replay Success",
    1: "Errors",
    2: "Unknown type",
    3: "Unknown term",
    4: "SMT-LIB parsing",
    5: "parsing error",
    7: "error replay",
    10: "Slurm timeout",
    11: "Checking timeout"
}

# Solver configs that should only appear in solving tables, not checking tables.
SOLVING_ONLY_CONFIGS = {"cpc", "verit_solving", "cvc5_solving"}


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkData:
    """All statistics extracted from the JSON entries."""

    solved_benchmarks: dict = field(default_factory=lambda: defaultdict(lambda: defaultdict(set)))
    line_stats: dict = field(default_factory=lambda: defaultdict(lambda: defaultdict(list)))
    time_stats: dict = field(default_factory=lambda: defaultdict(lambda: defaultdict(list)))
    time_per_benchmark: dict = field(default_factory=lambda: defaultdict(lambda: defaultdict(dict)))
    lines_per_benchmark: dict = field(default_factory=lambda: defaultdict(lambda: defaultdict(dict)))
    checking_counts: dict = field(default_factory=lambda: defaultdict(lambda: defaultdict(int)))
    checking_outcome_counts: dict = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    )  # library -> solver -> outcome_code -> count
    checking_time_stats: dict = field(default_factory=lambda: defaultdict(lambda: defaultdict(list)))
    checking_time_per_benchmark: dict = field(default_factory=lambda: defaultdict(lambda: defaultdict(dict)))
    checked_benchmarks: dict = field(default_factory=lambda: defaultdict(lambda: defaultdict(set)))  # library -> solver -> set of benchmarks with successful check
    all_benchmarks: dict = field(default_factory=lambda: defaultdict(set))


def load_data(file_path: str) -> list[dict]:
    """Load and return JSON entries from *file_path*."""
    with open(file_path) as f:
        try:
            return json.load(f)
        except Exception:
            print(f"Could not analyze, no entries found in: {file_path}")
            sys.exit(1)


def collect_statistics(entries: list[dict]) -> BenchmarkData:
    """Walk every JSON entry and accumulate statistics."""
    bd = BenchmarkData()

    for entry in entries:
        library = entry.get("library_name")
        benchmark = entry.get("benchmark_path")

        if library and benchmark:
            bd.all_benchmarks[library].add(benchmark)

        _collect_solving(entry, library, benchmark, bd)
        _collect_checking(entry, library, benchmark, bd)

    return bd

def apply_checking_time_limit(bd: BenchmarkData, limit: float):
    """Reclassify successful checks that exceeded *limit* seconds as failures (code 11)."""
    for library in list(bd.checking_time_per_benchmark.keys()):
        for solver in list(bd.checking_time_per_benchmark[library].keys()):
            for benchmark, t in list(bd.checking_time_per_benchmark[library][solver].items()):
                if t > limit:
                    # Only reclassify if it was a success (code 0)
                    if bd.checking_outcome_counts[library][solver].get(0, 0) > 0:
                        bd.checking_outcome_counts[library][solver][0] -= 1
                        bd.checking_outcome_counts[library][solver][11] += 1
                        bd.checking_counts[library][solver] -= 1
                        bd.checked_benchmarks[library][solver].discard(benchmark)


def _collect_solving(entry: dict, library: str, benchmark: str, bd: BenchmarkData):
    for s in entry.get("solving", []):
        solver = s.get("solver_config")
        outcome = s.get("solving_outcome")
        if outcome is None or outcome < 0:
            continue

        bd.solved_benchmarks[library][solver].add(benchmark)

        if "nr_of_lines" in s:
            lines = s["nr_of_lines"]
            bd.line_stats[library][solver].append(lines)
            bd.lines_per_benchmark[library][solver][benchmark] = lines

        if "solving_time" in s:
            #user_time = extract_user_time(s["solving_time"])
            try:
             user_time = float(s["solving_time"])/e^19
            except Exception:
             user_time = extract_user_time(s["solving_time"])
            if user_time is not None:
                bd.time_stats[library][solver].append(user_time)
                bd.time_per_benchmark[library][solver][benchmark] = user_time


def _collect_checking(entry: dict, library: str, benchmark: str, bd: BenchmarkData):
    for c in entry.get("checking", []):
        solver = c.get("solver_config")
        outcome = c.get("checking_outcome")
        if outcome is None:
            continue
        try:
            code = int(outcome)
        except (ValueError, TypeError):
            continue
        if code == 0:
            bd.checking_counts[library][solver] += 1
            bd.checked_benchmarks[library][solver].add(benchmark)

        if "checking_time" in c:
            checking_time = float(c["checking_time"])/100000000
            if checking_time is not None:
                bd.checking_time_stats[library][solver].append(checking_time)
                bd.checking_time_per_benchmark[library][solver][benchmark] = checking_time


        bd.checking_outcome_counts[library][solver][code] += 1


# ---------------------------------------------------------------------------
# Derived helpers
# ---------------------------------------------------------------------------

def all_libraries_and_solvers(bd: BenchmarkData):
    libraries = sorted(
        bd.solved_benchmarks.keys()
        | bd.checking_counts.keys()
        | bd.checking_outcome_counts.keys()
    )
    solvers = sorted(
        {s for lib in libraries
         for s in (bd.solved_benchmarks[lib].keys()
                   | bd.checking_counts[lib].keys()
                   | bd.checking_outcome_counts[lib].keys())}
    )
    return libraries, solvers


def has_any_solving(bd: BenchmarkData, libraries, solvers) -> bool:
    return any(
        len(bd.solved_benchmarks[lib][s]) > 0
        for lib in libraries for s in solvers
    )


def has_any_checking(bd: BenchmarkData, libraries, solvers) -> bool:
    return any(
        bd.checking_outcome_counts[lib][s]
        for lib in libraries for s in solvers
    )

def common_benchmarks(bd: BenchmarkData, library: str, solvers: list[str]) -> set:
    """Benchmarks solved by *all* solvers for a given library."""
    non_empty = [bd.solved_benchmarks[library][s] for s in solvers
                 if bd.solved_benchmarks[library][s]]
    if len(non_empty) >= 2:
        return set.intersection(*non_empty)
    return set()


def common_checked_benchmarks(bd: BenchmarkData, library: str, solvers: list[str]) -> set:
    """Benchmarks checked by *all* solvers for a given library."""
    non_empty = [set(bd.checking_time_per_benchmark[library][s].keys()) for s in solvers
                 if bd.checking_time_per_benchmark[library][s]]
    if len(non_empty) >= 2:
        return set.intersection(*non_empty)
    return set()

def unique_solved_benchmarks(bd: BenchmarkData, library: str, solvers: list[str]) -> dict:
    """Benchmarks solved by *only one* solver for a given library.
 
    Returns a dict mapping solver name -> set of benchmarks that only that
    solver solved (no other solver in *solvers* solved them).
    """
    result: dict[str, set] = {}
    for solver in solvers:
        own = bd.solved_benchmarks[library][solver]
        others = set()
        for other_solver in solvers:
            if other_solver != solver:
                others |= bd.solved_benchmarks[library][other_solver]
        result[solver] = own - others
    return result
 
def unique_checked_benchmarks(bd: BenchmarkData, library: str, solvers: list[str]) -> dict:
    """Benchmarks solved by all solvers but checked by *only one* solver for a given library.
 
    Returns a dict mapping solver name -> set of benchmarks where:
      1. Every solver in *solvers* solved the benchmark (i.e. it is in the common set).
      2. Only this solver had a successful check (checking_outcome == 0) for it.
    """
    common = common_benchmarks(bd, library, solvers)
    if not common:
        return {s: set() for s in solvers}
 
    # Build per-solver sets of benchmarks with successful checks among the common ones
    checked_by: dict[str, set] = {}
    for solver in solvers:
        checked = set()
        for b in common:
            outcomes = bd.checking_outcome_counts[library][solver]
            if b in outcomes:
                checked.add(b)
        checked_by[solver] = checked
 
    result: dict[str, set] = {}
    for solver in solvers:
        own = checked_by[solver]
        others = set()
        for other_solver in solvers:
            if other_solver != solver:
                others |= checked_by[other_solver]
        result[solver] = own - others
    return result

# ---------------------------------------------------------------------------
# Solver-level statistics (one row in the detailed table)
# ---------------------------------------------------------------------------

@dataclass
class SolverStats:
    solver: str
    solved_count: int = 0
    checked_ok: int = 0
    avg_lines: Optional[float] = None
    avg_common_lines: Optional[float] = None
    total_time: float = 0.0
    total_checking_time: float = 0.0
    total_common_time: Optional[float] = None
    total_common_checking_time: Optional[float] = None
    time_per_line: Optional[float] = None
    outcome_counts: dict = field(default_factory=dict)  # outcome_code -> count

def compute_solver_stats(
    bd: BenchmarkData, library: str, solver: str, common: set,
    common_checking: set | None = None,
) -> SolverStats:
    ss = SolverStats(solver=solver)
    ss.solved_count = len(bd.solved_benchmarks[library][solver])
    ss.checked_ok = bd.checking_counts[library][solver]
    ss.outcome_counts = dict(bd.checking_outcome_counts[library][solver])

    lines = bd.line_stats[library][solver]
    if lines:
        ss.avg_lines = sum(lines) / len(lines)

    solving_times = bd.time_stats[library][solver]
    ss.total_time = sum(solving_times)

    checking_times = bd.checking_time_stats[library][solver]
    ss.total_checking_time = sum(checking_times)

    common_lines = [
        bd.lines_per_benchmark[library][solver][b]
        for b in common if b in bd.lines_per_benchmark[library][solver]
    ]
    if common_lines:
        ss.avg_common_lines = sum(common_lines) / len(common_lines)

    common_solving_times = [
        bd.time_per_benchmark[library][solver][b]
        for b in common if b in bd.time_per_benchmark[library][solver]
    ]
    if common_solving_times:
        ss.total_common_time = sum(common_solving_times)

    common_checking_times = [
        bd.checking_time_per_benchmark[library][solver][b]
        for b in (common_checking if common_checking is not None else common)
        if b in bd.checking_time_per_benchmark[library][solver]
    ]
    if common_checking_times:
        ss.total_common_checking_time = sum(common_checking_times)

    if common_lines and ss.total_common_time:
        ss.time_per_line = 1000 * ss.total_common_time / sum(common_lines)

    return ss


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _fmt(value: Optional[float], fmt: str = ".2f") -> str:
    return f"{value:{fmt}}" if value is not None else "N/A"


def print_table(headers: list[tuple[str, str, int]], rows: list[list]):
    """Print an ASCII table given (label, align, width) headers and value rows."""
    header_line = " | ".join(f"{h:{a}{w}}" for h, a, w in headers)
    print(header_line)
    print("-" * len(header_line))
    for row in rows:
        print(" | ".join(
            f"{v:{a}{w}}" for v, (_, a, w) in zip(row, headers)
        ))


# ---------------------------------------------------------------------------
# Output modes
# ---------------------------------------------------------------------------

def print_summary(bd: BenchmarkData):
    libraries, solvers = all_libraries_and_solvers(bd)
    solving = has_any_solving(bd, libraries, solvers)
    checking = has_any_checking(bd, libraries, solvers)
    cw = 13

    # Build header
    sep = " | "  # must match print_table separator
    sep_w = len(sep)  # 3
    # Track which header indices belong to each solver
    solver_col_ranges = []

    headers = [("Library", "<", cw), ("Total", ">", cw)]
    for s in solvers:
        start=len(headers)
        is_solving_only = s in SOLVING_ONLY_CONFIGS
        if solving:
            headers.append((f"Nr solved", ">", cw))
        if checking and not is_solving_only:
            headers.append((f"Nr checked", ">", cw))
        if solving and checking and not is_solving_only:
            headers.append((f"Total Time", ">", cw))
        end=len(headers)
        solver_col_ranges.append((s, start, end))

    # Build solver name row aligned to column positions
    # First: width of fixed columns (Library + Total) plus their trailing separator
    fixed_width = sum(w for _, _, w in headers[:2]) + sep_w  # after last fixed col, separator into first group
    header0 = ' ' + ' ' * fixed_width + '|'
    for s, start, end in solver_col_ranges:
         ncols = end - start
         # Width of this group: column widths + separators between them + leading separator
         group_width = sum(w for _, _, w in headers[start:end]) + sep_w * (ncols - 1) + sep_w
         available_space = group_width - len(s) - 1  # -1 for the trailing '|'
         if available_space < 0:
            available_space = 0
         left = available_space // 2
         right = available_space - left
         header0 = header0 + ' ' * left + s + ' ' * right + '|'

    print(header0)
   
    rows = []
    for lib in libraries:
        common = common_benchmarks(bd, lib, solvers)

        row = [lib, len(bd.all_benchmarks[lib])]
        for s in solvers:
            is_solving_only = s in SOLVING_ONLY_CONFIGS
            #TODO: duplicate code, should be solidified
            common_solving_times = [
             bd.time_per_benchmark[lib][s][b]
             for b in common if b in bd.time_per_benchmark[lib][s]
            ]
            if common_solving_times:
              total_common_time = sum(common_solving_times)

            common_checking_times = [
               bd.checking_time_per_benchmark[lib][s][b]
               for b in common if b in bd.checking_time_per_benchmark[lib][s]
            ]
            if common_checking_times:
              total_common_checking_time = sum(common_checking_times)


            if solving:
                row.append(len(bd.solved_benchmarks[lib][s]))
            if checking and not is_solving_only:
                row.append(bd.checking_counts[lib][s])
            if solving and checking and not is_solving_only:
                if common_solving_times:
                  row.append(int(total_common_time+total_common_checking_time))
                else:
                  row.append("N/A")

        rows.append(row)

    print_table(headers, rows)
    print()
    print("Total Time is the time to produce the proof and check it on benchmark both solvers produced a proof for (common) in seconds")
    print()

def print_detailed(bd: BenchmarkData, output_csv: Optional[str] = None, library_filter: Optional[str] = None, config_filter: Optional[list[str]] = None):
    libraries, _ = all_libraries_and_solvers(bd)
    csv_rows: list[dict] = []
    if library_filter:
        libraries = [lib for lib in libraries if lib == library_filter]
        if not libraries:
            print(f"No data found for library: {library_filter}")
            return
    csv_rows: list[dict] = []

    solving_headers = [
        ("solver config",        "<", 18),
        ("total benchmarks",     ">", 18),
        ("nr benchmarks solved", ">", 21),
        ("avg nr_of_lines",      ">", 16),
        ("avg lines (common)",   ">", 20),
        ("total user time (s)",  ">", 18),
        ("total time (common)",  ">", 18),
    ]
    # Build checking headers 
    checking_headers1 = [("solver config", "<", 18), ("total benchmarks", ">", 18), ("nr_checked", ">", 18), ("total checking time",">",18), ("total checking time (common)",">",20)]
    checking_headers2 = [("solver config", "<", 18), ("benchmarks solved", ">", 18)]
    outcome_codes = sorted(CHECKING_OUTCOMES.keys())
    # Codes 2,3,4,5 are merged into a single "parsing error" display column.
    # The underlying data is still collected per-code in checking_outcome_counts.
    PARSING_ERROR_CODES = {2, 3, 4, 5}
    _parsing_col_added = False
    display_outcome_cols = []  # list of (label, codes_to_sum)
    for code in outcome_codes:
        if code in PARSING_ERROR_CODES:
            if not _parsing_col_added:
                display_outcome_cols.append(("parsing error", list(sorted(PARSING_ERROR_CODES))))
                _parsing_col_added = True
            continue
        display_outcome_cols.append((CHECKING_OUTCOMES[code], [code]))
    for label, _ in display_outcome_cols:
        if label == "Replay Success":
            width = 21
        else:
            width = max(len(label), 8) + 2
        checking_headers2.append((label, ">", width))

    for library in libraries:
        total = len(bd.all_benchmarks[library])
        print(f"Library: {library}  (total benchmarks: {total})\n")
        solvers = sorted(
            bd.solved_benchmarks[library].keys()
            | bd.checking_counts[library].keys()
            | bd.checking_outcome_counts[library].keys()
        )

        common = common_benchmarks(bd, library, solvers)
        # For checking-related "common" stats, only consider solvers that
        # actually participate in checking (exclude solving-only configs).
        checking_solvers = [s for s in solvers if s not in SOLVING_ONLY_CONFIGS]
        common_checking = common_checked_benchmarks(bd, library, checking_solvers)
        if config_filter:
            solvers = [s for s in solvers if s in config_filter]
            if not solvers:
                print("  (no matching solver configs)\n")
                continue

        # Compute stats for all solvers once
        all_stats = [compute_solver_stats(bd, library, s, common, common_checking) for s in solvers]

        lib_solving = any(ss.solved_count > 0 for ss in all_stats)
        lib_checking = any(ss.outcome_counts for ss in all_stats)

        if not lib_solving and not lib_checking:
            print("  (no data)\n")
            continue

        # Table 1: solving
        if lib_solving:
            solving_rows = []
            for ss in all_stats:
                if ss.solved_count == 0:
                    continue
                solving_rows.append([
                    ss.solver, total, ss.solved_count, _fmt(ss.avg_lines),
                    _fmt(ss.avg_common_lines), _fmt(ss.total_time),
                    _fmt(ss.total_common_time),
                ])
            print_table(solving_headers, solving_rows)
            print()

        # Table 2: checking overview
        if lib_checking:
            checking_rows = []
            for ss in all_stats:
                if ss.solver in SOLVING_ONLY_CONFIGS:
                    continue
                row = [ss.solver, total, ss.checked_ok, _fmt(ss.total_checking_time), _fmt(ss.total_common_checking_time)]
                checking_rows.append(row)
            print_table(checking_headers1, checking_rows)
            print()


        # Table 3: checking error details
        if lib_checking:
            checking_rows = []
            for ss in all_stats:
                if ss.solver in SOLVING_ONLY_CONFIGS:
                    continue
                if not any(ss.outcome_counts.get(c, 0) > 0 for c in outcome_codes):
                    continue
                row = [ss.solver,
                       ss.solved_count if ss.solved_count > 0
                       else sum(ss.outcome_counts.get(c, 0) for c in outcome_codes)]
                for _label, codes in display_outcome_cols:
                    row.append(sum(ss.outcome_counts.get(c, 0) for c in codes))
                checking_rows.append(row)
            print_table(checking_headers2, checking_rows)
            print()

        if output_csv:
            for ss in all_stats:
                if ss.solved_count > 0 or ss.checked_ok > 0:
                   csv_rows.append(_csv_dict(library, ss, total, lib_solving, lib_checking))


    if output_csv and csv_rows:
        _write_csv(output_csv, csv_rows)


def _csv_dict(library: str, ss: SolverStats, total_benchmarks: int, solving: bool, checking: bool) -> dict:
    return {
        "library": library,
        "total_benchmarks": total_benchmarks,
        "solver_config": ss.solver,
        "nr_benchmarks_solved": ss.solved_count if solving else "N/A",
        "avg_nr_of_lines": _fmt(ss.avg_lines) if solving else "N/A",
        "avg_lines_common": _fmt(ss.avg_common_lines) if solving else "N/A",
        "total_user_time_s": _fmt(ss.total_time) if solving else "N/A",
        "total_time_common": _fmt(ss.total_common_time) if solving else "N/A",
        "time_per_line": _fmt(ss.time_per_line) if solving else "N/A",
        "checked_ok": ss.checked_ok if checking else "N/A",
    }


CSV_FIELDS = [
    "library", "total_benchmarks", "solver_config", "nr_benchmarks_solved",
    "avg_nr_of_lines", "avg_lines_common", "total_user_time_s",
    "total_time_common", "time_per_line", "checked_ok",
]


def _write_csv(output_csv: str, rows: list[dict]):
    write_header = not os.path.exists(output_csv) or os.path.getsize(output_csv) == 0
    with open(output_csv, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)
    print(f"Results written to {output_csv}")


# ---------------------------------------------------------------------------
# Optional diagnostics
# ---------------------------------------------------------------------------

def report_cvc5_verit_line_diffs(bd: BenchmarkData, threshold: int = 10000):
    """Print benchmarks where cvc5 and verit line counts diverge significantly."""
    libraries, _ = all_libraries_and_solvers(bd)
    for library in libraries:
        cvc5_lines = bd.lines_per_benchmark[library].get("cvc5", {})
        verit_lines = bd.lines_per_benchmark[library].get("verit", {})
        for b in cvc5_lines:
            n_cvc5 = cvc5_lines.get(b)
            n_verit = verit_lines.get(b)
            if (n_cvc5 is not None and n_verit is not None
                    and abs(n_cvc5 - n_verit) >= threshold
                    and n_verit < 100):
                print(b)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None):
    parser = ArgumentParser(description="Analyze solver benchmark results.")
    parser.add_argument("file", help="Path to the JSON results file")
    parser.add_argument("-o", "--output-csv", help="Append results to a CSV file")
    parser.add_argument("-s", "--summary", action="store_true",
                        help="Print a compact summary table")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output")
    parser.add_argument("--line-diff", action="store_true",
                        help="Report large cvc5/verit line-count differences")
    parser.add_argument("--line-diff-threshold", type=int, default=10000,
                        help="Threshold for --line-diff (default: 10000)")
    parser.add_argument("-l", "--library", help="Filter results for a certain logic/library")
    parser.add_argument("-c", "--config", action="append",
                        help="Filter detailed view to specific solver config(s) (repeatable)")
    parser.add_argument("--checking-time-limit", type=float,
                        help="Count checks exceeding this time (seconds) as failures")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None):
    args = parse_args(argv)
    entries = load_data(args.file)
    bd = collect_statistics(entries)

    if args.checking_time_limit is not None:
        apply_checking_time_limit(bd, args.checking_time_limit)

    if args.line_diff:
        report_cvc5_verit_line_diffs(bd, threshold=args.line_diff_threshold)

    if args.summary:
        print_summary(bd)
    else:
        print_detailed(bd, output_csv=args.output_csv, library_filter=args.library, config_filter=args.config)


if __name__ == "__main__":
    main()
