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
The slowest checking times are left out because Isabelle's garbage collector runs at random times and makes some
checks slow. The solving times are not trimmed.
The configs are the ones occurring in the results, sorted by name. A second table below the legend shows the
proofs, common times and checking results with the configs next to each other, for comparing them. Each table is
followed by a legend of its columns.

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


def explanations(solving_key, checking_key):
    """Return the explanation of each column, by its key without the config ("Total" or (section, name))."""
    kind = {"cpu_time_s": "CPU time", "time_s": "wall time"}
    trim = f"{100 * CHECKING_TRIM:g}%"
    return {
        "Total": "number of benchmarks in the set",
        ("Solving", "Proofs"): "benchmarks solved with a proof (unsat)",
        ("Solving", "Time (s)"): f"total solving {kind[solving_key]} on these benchmarks",
        ("Solving", "Common (s)"): f"total solving {kind[solving_key]} on the benchmarks that all configs solved",
        ("Checking", "Reconstructed"): "proofs reconstructed successfully",
        ("Checking", "Error"): "proofs checked by Isabelle without success (failure, timeout, memout, ...)",
        ("Checking", "Time (s)"): f"total checking {kind[checking_key]} of the reconstructed proofs, "
                                  f"without the slowest {trim} of them (garbage collection makes some checks slow)",
        ("Checking", "Common (s)"): f"total checking {kind[checking_key]} on the benchmarks that all configs "
                                    f"reconstructed, without the slowest {trim} of them (by the maximal time over all "
                                    f"configs, the same benchmarks are left out for every config)",
    }


def legend(columns, explained):
    """Return the explanations of the columns, each column name only once (in all configs it means the same)."""
    lines = []
    for key, _, _ in columns:
        key = key if isinstance(key, str) else key[1:]
        if key not in explained:
            continue
        line = f"{key}: " if isinstance(key, str) else f"{key[0]} {key[1].removesuffix(' (s)')}: "
        line += explained[key]
        if line not in lines:
            lines.append(line)
    return lines


def make_table(results):
    """Return the configs, the rows (set, total, then the COLUMNS for each config) and the explanations of the
    columns."""
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
        row = {"Set": library, "Total": str(len(benchmarks))}
        for config in configs:
            s, c = solved[config], reconstructed[config]
            errors = [r for r in rs[config].values()
                      if r["checking"].get("status") not in NOT_CHECKED + ("success",)]
            values = [str(len(s)),
                      f"{sum(map(solving_time, s.values())):.1f}",
                      f"{sum(solving_time(s[p]) for p in common_solved):.1f}",
                      str(len(c)),
                      str(len(errors)),
                      f"{sum(trim_slowest(map(checking_time, c.values()))):.1f}",
                      f"{sum(checking_time(c[p]) for p in common_reconstructed):.1f}"]
            row.update({(config, section, name): v for (section, name), v in zip(COLUMNS, values)})
        rows.append(row)
    return configs, rows, explanations(solving_key, checking_key)


#A table layout is a list of columns (key in the rows of make_table, three header levels, markdown name). Adjacent
#columns with the same first (first two) header levels share a spanning header in the plain text output.
def base_columns():
    return [("Set", ("", "", "Set"), "Set"), ("Total", ("", "", "Total"), "Total")]


def columns_by_config(configs):
    """All COLUMNS of the first config, then of the second, ..."""
    return base_columns() + [((config, section, name), (config, section, name), f"{config} {section.lower()} {name}")
                             for config in configs for section, name in COLUMNS]


def columns_by_value(configs):
    """The number of proofs and the common times, with the configs next to each other."""
    def column(config, section, name, header):
        return (config, section, name), header, f"{config} {section.lower()} {name}"
    return (base_columns() +
            [column(c, "Solving", "Proofs", ("Solving", "Proofs", c)) for c in configs] +
            [column(c, "Solving", "Common (s)", ("Solving", "Common (s)", c)) for c in configs] +
            [column(c, "Checking", name, ("Checking", c, name)) for c in configs for name in ("Reconstructed", "Error")] +
            [column(c, "Checking", "Common (s)", ("Checking", "Common (s)", c)) for c in configs])


def format_text(columns, rows):
    """Return the table as aligned plain text, with the first two header levels as spanning headers."""
    headers = [header for _, header, _ in columns]
    names = [header[2] for header in headers]
    cells = [[row[key] for key, _, _ in columns] for row in rows]
    widths = [max(len(names[i]), *(len(row[i]) for row in cells)) for i in range(len(columns))]

    def sep(i):
        """Separator before column i: | where the spanning headers change, spaces otherwise."""
        return " | " if i >= 2 and headers[i][:2] != headers[i - 1][:2] else "  "

    def spans(level):
        """Spanning headers of the level as (text, first column, number of columns)."""
        result = []
        for i in range(2, len(columns)):
            if result and headers[i][:level + 1] == headers[i - 1][:level + 1]:
                result[-1][2] += 1
            else:
                result.append([headers[i][level], i, 1])
        return result

    def span_width(first, count):
        return sum(widths[first:first + count]) + sum(len(sep(i)) for i in range(first + 1, first + count))

    #Widen the last column of a span if its header does not fit
    for text, first, count in spans(0) + spans(1):
        widths[first + count - 1] += max(0, len(text) - span_width(first, count))

    def span_line(level):
        line = sep(1).join(" " * w for w in widths[:2])
        for text, first, count in spans(level):
            line += sep(first) + text.center(span_width(first, count))
        return line.rstrip()

    def line(cells, left_columns=1):
        out = ""
        for i, cell in enumerate(cells):
            out += (sep(i) if i else "") + (cell.ljust(widths[i]) if i < left_columns else cell.rjust(widths[i]))
        return out.rstrip()

    lines = [span_line(0), span_line(1), line(names, len(names)), line(["-" * w for w in widths], len(widths))]
    lines += [line(row) for row in cells]
    return "\n".join(lines)


def format_markdown(columns, rows):
    """Return the table as markdown. Markdown has no spanning headers, so the config and section are part of
    each column name."""
    names = [name for _, _, name in columns]
    rows = [[row[key] for key, _, _ in columns] for row in rows]
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
    configs, rows, explained = make_table(results)
    fmt = format_markdown if args.markdown else format_text
    for i, columns in enumerate((columns_by_config(configs), columns_by_value(configs))):
        if i:
            print()
            print("Proofs, common times and checking results with the configs next to each other:")
            print()
        print(fmt(columns, rows))
        print()
        print("\n".join(f"- {e}" if args.markdown else e for e in legend(columns, explained)))


if __name__ == "__main__":
    main()
