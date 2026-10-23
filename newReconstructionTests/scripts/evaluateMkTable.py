#!/usr/bin/env python3
"""Print a table of the solving (proof generation) and checking (proof reconstruction) results per set.

For each set (library, e.g. SMT2_0016) and config it lists:
  Solving  Proofs         benchmarks solved with a proof (unsat)
           Time (s)       total solving time on them
           Common (s)     total solving time on the benchmarks of the set that all configs solved
  Checking Reconstructed  proofs reconstructed successfully
           Error          proofs checked by Isabelle without success (failure, timeout, memout, ...)
           Time (s)       total checking time of the reconstructed proofs, without the slowest 5% of them
           Common (s)     total checking time on the benchmarks of the set that all configs reconstructed, without
                          the slowest 5% of them (by the maximal checking time over all configs, so the same
                          benchmarks are left out for every config)
The configs are the ones occurring in the results, sorted by name.

The times are CPU times (cpu_time_s), which do not include time spent waiting, e.g. for the file system. Results of
older versions of solveAndCheck.sh only have the wall time (time_s). If any solved or reconstructed benchmark lacks
the CPU time, the wall time is used for all of them, with a warning.

The inputs are read as by evaluate.py: results.json or results.json.gz files of submit-job.

Usage: evaluateMkTable.py [--markdown] <results.json or results.json.gz>...
"""

import argparse
import sys
from collections import defaultdict

from evaluate import CHECKING_TRIM, NOT_CHECKED, collect, trim_slowest

#(section, column name) of the columns shown for each config
COLUMNS = [("Solving", "Proofs"), ("Solving", "Time (s)"), ("Solving", "Common (s)"),
           ("Checking", "Reconstructed"), ("Checking", "Error"), ("Checking", "Time (s)"),
           ("Checking", "Common (s)")]


def time_key(records, step):
    """Return the key of the time to use for step ("solving" or "checking") of records."""
    if all("cpu_time_s" in r[step] for r in records):
        return "cpu_time_s"
    print(f"Warning: not all {step} results have a CPU time (cpu_time_s), using the wall time (time_s)",
          file=sys.stderr)
    return "time_s"


def legend(solving_key, checking_key):
    trim = f"{100 * CHECKING_TRIM:g}%"
    kind = {"cpu_time_s": "CPU time", "time_s": "wall time"}
    return [
        "Total: number of benchmarks in the set",
        "Solving Proofs: benchmarks solved with a proof (unsat)",
        f"Solving Time: total solving {kind[solving_key]} on these benchmarks",
        f"Solving Common: total solving {kind[solving_key]} on the benchmarks that all configs solved",
        "Checking Reconstructed: proofs reconstructed successfully",
        "Checking Error: proofs checked by Isabelle without success (failure, timeout, memout, ...)",
        f"Checking Time: total checking {kind[checking_key]} of the reconstructed proofs, "
        f"without the slowest {trim} of them",
        f"Checking Common: total checking {kind[checking_key]} on the benchmarks that all configs reconstructed, "
        f"without the slowest {trim} of them (by the maximal time over all configs, the same benchmarks are left "
        f"out for every config)",
    ]


def make_table(results):
    """Return the configs, the rows (set, total, then the COLUMNS for each config) and the legend."""
    #library -> config -> benchmark path -> result
    sets = defaultdict(lambda: defaultdict(dict))
    for r in results:
        sets[r.get("library_name", "N/A")][r.get("config")][r.get("benchmark_path")] = r
    configs = sorted({r.get("config") for r in results})

    solving_key = time_key([r for r in results if r["solving"].get("status") == "unsat"], "solving")
    checking_key = time_key([r for r in results if r["checking"].get("status") == "success"], "checking")

    def solving_time(r):
        return r["solving"].get(solving_key) or 0

    def checking_time(r):
        return r["checking"].get(checking_key) or 0

    rows = []
    for library, by_config in sorted(sets.items()):
        benchmarks = set().union(*(rs.keys() for rs in by_config.values()))
        rs = {config: by_config.get(config, {}) for config in configs}
        solved = {config: {p: r for p, r in rs[config].items() if r["solving"].get("status") == "unsat"}
                  for config in configs}
        reconstructed = {config: {p: r for p, r in rs[config].items() if r["checking"].get("status") == "success"}
                         for config in configs}
        common_solved = set.intersection(*(set(s) for s in solved.values()))
        common_reconstructed = sorted(set.intersection(*(set(s) for s in reconstructed.values())),
                                      key=lambda p: max(checking_time(reconstructed[c][p]) for c in configs))
        common_reconstructed = common_reconstructed[:len(common_reconstructed) -
                                                    int(len(common_reconstructed) * CHECKING_TRIM)]
        row = [library, str(len(benchmarks))]
        for config in configs:
            s, c = solved[config], reconstructed[config]
            errors = [r for r in rs[config].values()
                      if r["checking"].get("status") not in NOT_CHECKED + ("success",)]
            row += [str(len(s)),
                    f"{sum(map(solving_time, s.values())):.1f}",
                    f"{sum(solving_time(s[p]) for p in common_solved):.1f}",
                    str(len(c)),
                    str(len(errors)),
                    f"{sum(trim_slowest(map(checking_time, c.values()))):.1f}",
                    f"{sum(checking_time(c[p]) for p in common_reconstructed):.1f}"]
        rows.append(row)
    return configs, rows, legend(solving_key, checking_key)


def format_text(configs, rows):
    """Return the table as aligned plain text, with the configs and sections as spanning headers."""
    names = ["Set", "Total"] + [name for _ in configs for _, name in COLUMNS]
    widths = [max(len(names[i]), *(len(row[i]) for row in rows)) for i in range(len(names))]
    #Spanning headers: (text, first column, number of columns)
    nr = len(COLUMNS)
    nr_solving = sum(1 for section, _ in COLUMNS if section == "Solving")
    config_spans = [(config, 2 + i * nr, nr) for i, config in enumerate(configs)]
    section_spans = [span for i in range(len(configs))
                     for span in (("Solving", 2 + i * nr, nr_solving),
                                  ("Checking", 2 + i * nr + nr_solving, nr - nr_solving))]

    def sep(i):
        """Separator before column i: | between configs and sections, spaces otherwise."""
        return " | " if i >= 2 and (i - 2) % nr in (0, nr_solving) else "  "

    def span_width(first, count):
        return sum(widths[first:first + count]) + sum(len(sep(i)) for i in range(first + 1, first + count))

    #Widen the last column of a span if its header does not fit
    for text, first, count in config_spans + section_spans:
        widths[first + count - 1] += max(0, len(text) - span_width(first, count))

    def span_line(spans):
        line = sep(0).join(" " * w for w in widths[:2])
        for text, first, count in spans:
            line += sep(first) + text.center(span_width(first, count))
        return line.rstrip()

    def line(cells, left_columns=1):
        out = ""
        for i, cell in enumerate(cells):
            out += (sep(i) if i else "") + (cell.ljust(widths[i]) if i < left_columns else cell.rjust(widths[i]))
        return out.rstrip()

    lines = [span_line(config_spans), span_line(section_spans), line(names, len(names)),
             line(["-" * w for w in widths], len(widths))]
    lines += [line(row) for row in rows]
    return "\n".join(lines)


def format_markdown(configs, rows):
    """Return the table as markdown. Markdown has no spanning headers, so the config and section are part of
    each column name."""
    names = ["Set", "Total"] + [f"{config} {section.lower()} {name}" for config in configs for section, name in COLUMNS]
    widths = [max(len(names[i]), *(len(row[i]) for row in rows), 3) for i in range(len(names))]

    def line(cells, left_columns=1):
        return "| " + " | ".join(cell.ljust(w) if i < left_columns else cell.rjust(w)
                                 for i, (cell, w) in enumerate(zip(cells, widths))) + " |"

    align = [":" + "-" * (widths[0] - 1)] + ["-" * (w - 1) + ":" for w in widths[1:]]
    return "\n".join([line(names, len(names)), line(align)] + [line(row) for row in rows])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="+", help="results files (.json or .json.gz)")
    parser.add_argument("--markdown", action="store_true", help="print the table as markdown")
    args = parser.parse_args()

    results, nr_tasks = collect(args.inputs)
    if nr_tasks == 0:
        print("No task records found", file=sys.stderr)
        sys.exit(1)
    configs, rows, explanations = make_table(results)
    if args.markdown:
        print(format_markdown(configs, rows))
        print()
        print("\n".join(f"- {e}" for e in explanations))
    else:
        print(format_text(configs, rows))
        print()
        print("\n".join(explanations))


if __name__ == "__main__":
    main()
