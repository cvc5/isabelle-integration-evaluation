#!/usr/bin/env python3
import json
import sys
import csv
from collections import defaultdict
import os
from argparse import ArgumentParser
import shutil

#written by ChatGpt, modified by Claude

def extract_user_time(solving_time):
    try:
        for part in solving_time.split():
            if part.endswith("user"):
                return float(part.replace("user", ""))
    except Exception:
        pass
    return None

def analyze(file_path, output_csv=None, summary=False):
    with open(file_path) as f:
        try:
            data = json.load(f)
        except Exception:
            print("Could not analyze, no entries found in: ", file_path)
            sys.exit(1)

    solved_benchmarks = defaultdict(lambda: defaultdict(set))
    line_stats = defaultdict(lambda: defaultdict(list))
    time_stats = defaultdict(lambda: defaultdict(list))
    time_per_benchmark = defaultdict(lambda: defaultdict(dict))
    lines_per_benchmark = defaultdict(lambda: defaultdict(dict))
    checking_counts = defaultdict(lambda: defaultdict(int))

    all_benchmarks = defaultdict(set)

    for entry in data:
        library = entry.get("library_name")
        benchmark = entry.get("benchmark_path")
        if library and benchmark:
            all_benchmarks[library].add(benchmark)
        for s in entry.get("solving", []):
            solver = s.get("solver_config")
            outcome = s.get("solving_outcome")
            if outcome is not None and outcome >= 0:
                solved_benchmarks[library][solver].add(benchmark)
                if "nr_of_lines" in s:
                    lines = s["nr_of_lines"]
                    line_stats[library][solver].append(lines)
                    lines_per_benchmark[library][solver][benchmark] = lines
                if "solving_time" in s:
                    user_time = extract_user_time(s["solving_time"])
                    if user_time is not None:
                        time_stats[library][solver].append(user_time)
                        time_per_benchmark[library][solver][benchmark] = user_time
        for c in entry.get("checking", []):
            solver = c.get("solver_config")
            checking_outcome = c.get("checking_outcome")
            if checking_outcome is not None and str(checking_outcome) == "0":
                checking_counts[library][solver] += 1

    if summary:
        all_libraries = sorted(solved_benchmarks.keys() | checking_counts.keys())
        all_solvers = sorted(
            {s for lib in all_libraries for s in (solved_benchmarks[lib].keys() | checking_counts[lib].keys())}
        )

        col_width = 20
        header_parts = [f"{'Library':<20}", f"{'Total':>{col_width}}"]
        for solver in all_solvers:
            header_parts.append(f"{'Nr solved ' + solver:>{col_width}}")
            header_parts.append(f"{'Nr checked ' + solver:>{col_width}}")
        header = " | ".join(header_parts)
        print(header)
        print("-" * len(header))

        for library in all_libraries:
            row_parts = [f"{library:<20}"]
            total = len(all_benchmarks[library])
            row_parts.append(f"{total:>{col_width}}")
            for solver in all_solvers:
                solved_count = len(solved_benchmarks[library][solver])
                checked_ok   = checking_counts[library][solver]
                row_parts.append(f"{solved_count:>{col_width}}")
                row_parts.append(f"{checked_ok:>{col_width}}")
            print(" | ".join(row_parts))
        return

    columns = [
        ("solver config",        "<", 18, lambda: solver),
        ("nr benchmarks solved", ">", 21, lambda: solved_count),
        ("avg nr_of_lines",      ">", 16, lambda: avg_lines_str),
        ("avg lines (common)",   ">", 20, lambda: avg_common_lines_str),
        ("total user time (s)",  ">", 18, lambda: total_time_str),
        ("total time (common)",  ">", 18, lambda: total_common_time_str),
        ("checked ok",           ">", 12, lambda: checked_ok),
    ]

    def select_columns(names):
        lookup = {col[0]: col for col in columns}
        return [lookup[name] for name in names]

    def get_values(cols):
        return [(*col[:3], col[3]()) for col in cols]

    columns_both     = [col[:3] for col in columns]
    columns_solving  = select_columns(["solver config", "nr benchmarks solved", "avg nr_of_lines", "avg lines (common)", "total user time (s)", "total time (common)"])
    columns_checking = select_columns(["solver config", "checked ok"])

    csv_rows = []

    all_libraries = sorted(solved_benchmarks.keys() | checking_counts.keys())
    for library in all_libraries:
        print(f"Library: {library}\n")

        solvers = sorted(solved_benchmarks[library].keys() | checking_counts[library].keys())
        if len(solvers) >= 2:
            common = set.intersection(
                *(solved_benchmarks[library][s] for s in solvers if solved_benchmarks[library][s])
            ) if any(solved_benchmarks[library][s] for s in solvers) else set()
        else:
            common = set()

        # Determine which cases are present across all solvers for this library
        has_solving  = any(len(solved_benchmarks[library][s]) > 0 for s in solvers)
        has_checking = any(checking_counts[library][s] > 0 for s in solvers)

        if has_solving and has_checking:
            columns = columns_both
        elif has_solving:
            columns = columns_solving
        elif has_checking:
            columns = columns_checking
        else:
            print("  (no data)\n")
            continue

        header = " | ".join(f"{label:{align}{width}}" for label, align, width in columns)
        print(header)
        print("-" * len(header))

        for solver in solvers:
            solved_count = len(solved_benchmarks[library][solver])
            checked_ok   = checking_counts[library][solver]

            lines = line_stats[library][solver]
            avg_lines = sum(lines) / len(lines) if lines else None
            times = time_stats[library][solver]
            total_time = sum(times)

            common_lines = [
                lines_per_benchmark[library][solver][b]
                for b in common
                if b in lines_per_benchmark[library][solver]
            ]
            avg_common_lines = sum(common_lines) / len(common_lines) if common_lines else None

            common_times = [
                time_per_benchmark[library][solver][b]
                for b in common
                if b in time_per_benchmark[library][solver]
            ]
            total_common_time = sum(common_times) if common_times else None

            avg_lines_str = f"{avg_lines:.2f}" if avg_lines is not None else "N/A"
            avg_common_lines_str = f"{avg_common_lines:.2f}" if avg_common_lines is not None else "N/A"
            total_time_str = f"{total_time:.2f}" if total_time is not None else "N/A"
            total_common_time_str = f"{total_common_time:.2f}" if total_common_time is not None else "N/A"

            time_per_line = 1000*total_common_time/sum(common_lines) if common_lines and total_common_time else None
            time_per_line_str = f"{time_per_line:.2f}" if time_per_line is not None else "N/A"

            if has_solving and has_checking:
                if solved_count == 0 and checked_ok == 0:
                    continue
                values = [
                    (solver,                "<", 18),
                    (solved_count,          ">", 21),
                    (avg_lines_str,         ">", 16),
                    (avg_common_lines_str,  ">", 20),
                    (total_time_str,        ">", 18),
                    (total_common_time_str, ">", 18),
                    (checked_ok,            ">", 12),
                ]
            elif has_solving:
                if solved_count == 0:
                    continue
                values = [
                    (solver,                "<", 18),
                    (solved_count,          ">", 21),
                    (avg_lines_str,         ">", 16),
                    (avg_common_lines_str,  ">", 20),
                    (total_time_str,        ">", 18),
                    (total_common_time_str, ">", 18),
                ]
            else:  # has_checking only
                if checked_ok == 0:
                    continue
                values = [
                    (solver,     "<", 18),
                    (checked_ok, ">", 12),
                ]

            print(" | ".join(f"{val:{align}{width}}" for val, align, width in values))

            if output_csv:
                csv_rows.append({
                    "library": library,
                    "solver_config": solver,
                    "nr_benchmarks_solved": solved_count if has_solving else "N/A",
                    "avg_nr_of_lines": avg_lines_str if has_solving else "N/A",
                    "avg_lines_common": avg_common_lines_str if has_solving else "N/A",
                    "total_user_time_s": total_time_str if has_solving else "N/A",
                    "total_time_common": total_common_time_str if has_solving else "N/A",
                    "time_per_line": time_per_line_str if has_solving else "N/A",
                    "checked_ok": checked_ok if has_checking else "N/A",
                })

        print()

        if output_csv and csv_rows:
            with open(output_csv, "a", newline="") as f:
                fieldnames = ["library", "solver_config", "nr_benchmarks_solved",
                          "avg_nr_of_lines", "avg_lines_common", "total_user_time_s", "total_time_common", "time_per_line", "checked_ok"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not os.path.exists(output_csv):  #TODO: Not working
                    writer.writeheader()
                writer.writerows(csv_rows)
            print(f"Results written to {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze solved benchmarks per library.")
    parser.add_argument("file", help="Path to merged JSON file")
    parser.add_argument("-o", nargs="?", const="result.csv", default=None,
                        help="Write results to a CSV file (default: result.csv)")
    parser.add_argument("-s", action="store_true",
                        help="Use alternative summary printing")
    args = parser.parse_args()
    analyze(args.file, output_csv=args.o, summary=args.s)
