#!/usr/bin/env python3
"""Print a table of the proof generation (solving) results per set, tab separated.

For each set (library, e.g. SMT2_0016) and config it lists the number of benchmarks solved with a proof (unsat),
the total solving time on them, and the total solving time on the benchmarks of the set that all configs solved.
The configs are the ones occurring in the results, sorted by name.

The inputs are read as by evaluate.py: results.json files of submit-job, or directories containing them.

Usage: evaluateMkTable.py <results.json or results dir>...
"""

import argparse
import sys
from collections import defaultdict

from evaluate import collect


def solving_time(r):
    return r["solving"].get("time_s") or 0


def make_table(results):
    #library -> config -> benchmark path -> result
    sets = defaultdict(lambda: defaultdict(dict))
    for r in results:
        sets[r.get("library_name", "N/A")][r.get("config")][r.get("benchmark_path")] = r
    configs = sorted({r.get("config") for r in results})

    rows = [
        ["Set", "Total", "Solving (Generating proof certificates)"] + [""] * (3 * len(configs) - 1),
        ["", ""] + [cell for config in configs for cell in (config, "", "")],
        ["", ""] + ["Nr proof generated", "Total Time (s)", "Total Time Common (s)"] * len(configs),
    ]
    for library, by_config in sorted(sets.items()):
        benchmarks = set().union(*(rs.keys() for rs in by_config.values()))
        solved = {config: {path: r for path, r in by_config.get(config, {}).items()
                           if r["solving"].get("status") == "unsat"}
                  for config in configs}
        common = set.intersection(*(set(s) for s in solved.values()))
        row = [library, str(len(benchmarks))]
        for config in configs:
            s = solved[config]
            row += [str(len(s)),
                    f"{sum(map(solving_time, s.values())):.1f}",
                    f"{sum(solving_time(s[path]) for path in common):.1f}"]
        rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="+", help="results.json files or results directories")
    args = parser.parse_args()

    results, nr_tasks = collect(args.inputs)
    if nr_tasks == 0:
        print("No task records found", file=sys.stderr)
        sys.exit(1)
    for row in make_table(results):
        print("\t".join(row))


if __name__ == "__main__":
    main()
