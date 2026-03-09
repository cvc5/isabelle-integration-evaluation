#!/usr/bin/env python3
import json
import sys
import csv
import argparse
from collections import defaultdict
import os

#written by ChatGpt, modified by Claude
#adapted

def analyze(file_path, output_csv=None):
    with open(file_path) as f:
        try:
            data = json.load(f)
        except Exception:
            print("Could not analyze, no entries found in: ", file_path)
            sys.exit(1)

    reconstructed_benchmarks = defaultdict(lambda: defaultdict(set))
    #time_per_benchmark = defaultdict(lambda: defaultdict(dict))
    #lines_per_benchmark = defaultdict(lambda: defaultdict(dict))

    for entry in data:
        library = entry.get("library_name")
        benchmark = entry.get("benchmark_path")
        for s in entry.get("checking", []):
            solver = s.get("solver_config")
            outcome = s.get("checking_outcome")
            if outcome is not None and outcome != '':
             if int(outcome) == 0:
                reconstructed_benchmarks[library][solver].add(benchmark)
                #if "checking_time" in s:
                #    user_time = extract_user_time(s["solving_time"])
                #    if user_time is not None:
                #        time_stats[library][solver].append(user_time)
                #        time_per_benchmark[library][solver][benchmark] = user_time

    csv_rows = []

    for library in sorted(reconstructed_benchmarks):
        print(f"Library: {library}\n")
        print(
            f"{'solver config':<18} | "
            f"{'nr benchmarks reconstructed':>25} | "
            #f"{'total user time (s)':>18} | "
            #f"{'total time (common)':>18}"
        )
        print("-" * (18 + 3 + 25 + 3 ))

        solvers = sorted(reconstructed_benchmarks[library])
        if len(solvers) >= 2:
            common = set.intersection(
                *(reconstructed_benchmarks[library][s] for s in solvers)
            )
        else:
            common = set()

        for solver in solvers:
            reconstructed_count = len(reconstructed_benchmarks[library][solver])

            #times = time_stats[library][solver]
            #avg_time = sum(times) / len(times) if times else None
            #total_time = sum(times)

            #common_times = [
            #    time_per_benchmark[library][solver][b]
            #    for b in common
            #    if b in time_per_benchmark[library][solver]
            #]
            #total_common_time = sum(common_times) if common_times else None
            #avg_common_time = sum(common_times) / len(common_times) if common_times else None

            #avg_time_str = f"{avg_time:.2f}" if avg_time is not None else "N/A"
            #avg_common_time_str = f"{avg_common_time:.2f}" if avg_common_time is not None else "N/A"
            #total_time_str = f"{total_time:.2f}" if total_time is not None else "N/A"
            #total_common_time_str = f"{total_common_time:.2f}" if total_common_time is not None else "N/A"

            print(
                f"{solver:<18} | "
                f"{reconstructed_count:>25} | "
                #f"{total_time_str:>18} | "
                #f"{avg_common_time_str:>18}"
                #f"{total_common_time_str:>18}"
            )

            if output_csv:
                csv_rows.append({
                    "library": library,
                    "solver_config": solver,
                    "nr_benchmarks_reconstructed": reconstructed_count,
                    #"total_user_time_s": total_time_str,
                    #"avg_user_time_s": avg_time_str,
                    #"total_time_common": total_common_time_str,
                })

        print()

        if output_csv and csv_rows:
         with open(output_csv, "a", newline="") as f:
            fieldnames = ["library", "solver_config", "nr_benchmarks_reconstructed"]
            if not os.path.exists(output_csv): #TODO: Not working
              writer.writeheader()
            writer.writerows(csv_rows)
         print(f"Results written to {output_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze solved benchmarks per library.")
    parser.add_argument("file", help="Path to merged JSON file")
    parser.add_argument("-o", nargs="?", const="result.csv", default=None,
                    help="Write results to a CSV file (default: test.csv)")
    args = parser.parse_args()
    analyze(args.file, output_csv=args.o)
