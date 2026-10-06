#!/usr/bin/env python3
"""Compare the reconstruction results of two solver configs (default cvc5 vs veriT).

Reads the results.json written by submit-job and prints, per library and in total:
  a) how many benchmarks could be reconstructed (solved and checked successfully) with each config,
     and how many more with the first config than with the second
  b) the average solving + reconstruction time per config on the benchmarks that both configs solved
     and reconstructed, and how much faster/slower the first config is

Only benchmarks with a result for both configs are compared. Benchmarks where a result is missing
(e.g. the job crashed or hit the slurm timeout) are left out and their number is reported.

Usage: makeTablePresentation.py [-a cvc5] [-b verit] [--latex] <results.json>
"""

import argparse
import math
import sys
from collections import defaultdict
from pathlib import Path

#Reuse the parser of evaluate.py for the submit-job output
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import evaluate


def complete(configs, a, b):
    """True if both configs have a result for this benchmark."""
    return all(c in configs and configs[c]["solving"].get("status") != "missing" for c in (a, b))


def total_time(result):
    return result["solving"]["time_s"] + result["checking"]["time_s"]


def reconstructed(result):
    return result is not None and result.get("checking", {}).get("status") == "success"


def compare(results, a, b):
    """results: benchmark_path -> config -> result. Returns one row of the table."""
    rec_a = {p for p, r in results.items() if reconstructed(r.get(a))}
    rec_b = {p for p, r in results.items() if reconstructed(r.get(b))}
    both = rec_a & rec_b

    #Only compare times on benchmarks both configs reconstructed, otherwise the sets differ
    times_a = [total_time(results[p][a]) for p in both]
    times_b = [total_time(results[p][b]) for p in both]
    avg_a = sum(times_a) / len(both) if both else None
    avg_b = sum(times_b) / len(both) if both else None
    #Geometric mean of the per benchmark ratios, less dominated by a few long running benchmarks
    ratios = [ta / tb for ta, tb in zip(times_a, times_b) if ta > 0 and tb > 0]
    geo_ratio = math.exp(sum(map(math.log, ratios)) / len(ratios)) if ratios else None

    return {
        "benchmarks": len(results),
        "rec_a": len(rec_a), "rec_b": len(rec_b), "diff": len(rec_a) - len(rec_b),
        "only_a": len(rec_a - rec_b), "only_b": len(rec_b - rec_a), "both": len(both),
        "avg_a": avg_a, "avg_b": avg_b,
        "avg_ratio": avg_a / avg_b if both and avg_b else None,
        "geo_ratio": geo_ratio,
    }


def fmt(value, spec):
    return "-" if value is None else format(value, spec)


def speed(ratio):
    """Describe ratio = time_a / time_b in words."""
    if ratio is None:
        return "-"
    if ratio <= 1:
        return f"{(1 - ratio) * 100:.1f}% faster"
    return f"{(ratio - 1) * 100:.1f}% slower"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("result_file", help="results.json written by submit-job")
    parser.add_argument("-a", default="cvc5", help="first config (default cvc5)")
    parser.add_argument("-b", default="verit", help="second config (default verit)")
    parser.add_argument("--latex", action="store_true", help="print a LaTeX table instead of a Markdown table")
    args = parser.parse_args()
    a, b = args.a, args.b

    if not Path(args.result_file).is_file():
        print(f"Error: {args.result_file} is not a file", file=sys.stderr)
        sys.exit(1)
    data, nr_tasks = evaluate.collect([args.result_file])
    if nr_tasks == 0:
        print("No task records in " + args.result_file, file=sys.stderr)
        sys.exit(1)

    #library -> benchmark_path -> config -> result
    by_library = defaultdict(lambda: defaultdict(dict))
    for r in data:
        by_library[r.get("library_name", "N/A")][r["benchmark_path"]][r["config"]] = r

    #Only compare benchmarks for which both configs have a result
    excluded = 0
    for lib, results in by_library.items():
        incomplete = [p for p, configs in results.items() if not complete(configs, a, b)]
        excluded += len(incomplete)
        for p in incomplete:
            del results[p]
    by_library = {lib: results for lib, results in by_library.items() if results}
    print(f"Read {nr_tasks} tasks. Left out {excluded} benchmarks without a result for both {a} and {b}.",
          file=sys.stderr)
    if not by_library:
        print("No benchmarks with results for both configs", file=sys.stderr)
        sys.exit(1)

    rows = [(lib, compare(results, a, b)) for lib, results in sorted(by_library.items())]
    if len(rows) > 1:
        everything = {}
        for lib, results in by_library.items():
            everything.update({(lib, p): r for p, r in results.items()})
        rows.append(("Total", compare(everything, a, b)))

    header = ["Library", "Benchmarks", f"Reconstructed {a}", f"Reconstructed {b}", f"{a} - {b}",
              f"Only {a}", f"Only {b}", "Both",
              f"Avg. time {a} (s)", f"Avg. time {b} (s)", f"{a} vs. {b} (avg.)", f"{a} vs. {b} (geo. mean)"]
    lines = []
    for lib, c in rows:
        lines.append([lib, str(c["benchmarks"]), str(c["rec_a"]), str(c["rec_b"]), f"{c['diff']:+d}",
                      str(c["only_a"]), str(c["only_b"]), str(c["both"]),
                      fmt(c["avg_a"], ".2f"), fmt(c["avg_b"], ".2f"), speed(c["avg_ratio"]), speed(c["geo_ratio"])])

    if args.latex:
        print("\\begin{tabular}{l" + "r" * (len(header) - 1) + "}")
        print("\\toprule")
        print(" & ".join(header) + " \\\\")
        print("\\midrule")
        for line in lines:
            if line[0] == "Total":
                print("\\midrule")
            print(" & ".join(x.replace("%", "\\%") for x in line) + " \\\\")
        print("\\bottomrule")
        print("\\end{tabular}")
    else:
        print("| " + " | ".join(header) + " |")
        print("|" + "|".join("---" if i == 0 else "---:" for i in range(len(header))) + "|")
        for line in lines:
            print("| " + " | ".join(line) + " |")

    print()
    print(f"Times are solving + reconstruction, averaged over the benchmarks solved and reconstructed by both "
          f"{a} and {b}.", file=sys.stderr)


if __name__ == "__main__":
    main()
