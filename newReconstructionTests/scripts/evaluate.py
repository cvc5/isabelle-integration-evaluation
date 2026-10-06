#!/usr/bin/env python3
"""Collect the results of solveAndCheckWrapper.sh runs and print a summary.

Reads all task records written by submit-job (files containing JSON objects with "type": "task",
either one object per file, one per line, or a JSON array) below the given directories. Every
"RESULT_JSON: {...}" line in a task's output_log becomes one result. Configs that were requested
with -c but have no result (crash, slurm timeout, missing binary, ...) are added with status "missing".

Usage: evaluate.py [-o combined.json] [--csv results.csv] <results dir or file>...
"""

import argparse
import csv
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

RESULT_PREFIX = "RESULT_JSON: "
SEPARATOR = "-" * 80


def read_json_objects(path):
    """Yield all JSON objects in a file (single object, JSON array, or JSON lines)."""
    try:
        text = path.read_text(errors="replace")
    except OSError as e:
        print(f"Warning: cannot read {path}: {e}", file=sys.stderr)
        return
    try:
        data = json.loads(text)
        if isinstance(data, list):
            yield from (d for d in data if isinstance(d, dict))
        elif isinstance(data, dict):
            yield data
        return
    except json.JSONDecodeError:
        pass
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            pass


def parse_run_log(run_log):
    """Extract host, times and memory from the submit-job run log."""
    info = {}
    for line in run_log.splitlines():
        if line.startswith("c host:"):
            info["host"] = line.split(":", 1)[1].strip()
        elif line.startswith("c command:"):
            info["command"] = line.split(":", 1)[1].strip()
        elif "=" in line and not line.startswith("c "):
            key, value = line.split("=", 1)
            if key == "returnvalue":
                info["returnvalue"] = int(value)
            elif key == "walltime":
                info["walltime_s"] = round(float(value.rstrip("s")), 3)
            elif key == "cputime":
                info["cputime_s"] = round(float(value.rstrip("s")), 3)
            elif key == "memory":
                info["memory_mb"] = round(int(value.rstrip("B")) / 2**20, 1)
    return info


def requested_configs(command):
    """Configs passed with -c to solveAndCheck.sh, defaults as in the script."""
    configs = re.findall(r"(?:^|\s)-c\s+(\S+)", command)
    return configs or ["cvc5", "verit"]


def results_of_task(task):
    """Return the result records of one task, including "missing" ones."""
    output_log = task.get("output_log", "")
    run_info = parse_run_log(task.get("run_log", ""))
    job = {"job_id": task.get("job_id"), "task_id": task.get("id")}
    job.update({k: v for k, v in run_info.items() if k != "command"})

    #The output log starts with the command, followed by a separator line
    command = run_info.get("command") or output_log.split("\n", 1)[0]
    body = output_log.split(SEPARATOR, 1)[1] if SEPARATOR in output_log else output_log

    results = []
    other_lines = []
    for line in body.splitlines():
        if line.startswith(RESULT_PREFIX):
            try:
                results.append(json.loads(line[len(RESULT_PREFIX):]))
            except json.JSONDecodeError:
                other_lines.append(line)
        elif line.strip():
            other_lines.append(line)

    for r in results:
        r["job"] = job
        if other_lines:
            r["job_messages"] = other_lines

    #Add configs without a result
    found = {r.get("config") for r in results}
    benchmark_path = task.get("job_args", "").strip()
    #The last two arguments of solveAndCheck.sh are base_dir and the benchmark
    args = command.split()
    base_dir = args[-2].rstrip("/") + "/" if len(args) >= 2 else ""
    relative_path = benchmark_path[len(base_dir):] if benchmark_path.startswith(base_dir) else benchmark_path
    for config in requested_configs(command):
        if config not in found:
            results.append({
                "benchmark_name": Path(benchmark_path).stem,
                "benchmark_path": benchmark_path,
                "relative_benchmark_path": relative_path,
                "library_name": (re.search(r"(?:^|\s)-l\s+(\S+)", command) or [None, "N/A"])[1],
                "config": config,
                "solving": {"status": "missing"},
                "checking": {"status": "missing"},
                "job": job,
                "job_messages": other_lines,
            })
    return results


def collect(paths):
    files = []
    for p in map(Path, paths):
        if p.is_dir():
            files.extend(sorted(f for f in p.rglob("*") if f.is_file()))
        elif p.is_file():
            files.append(p)
        else:
            print(f"Warning: {p} does not exist", file=sys.stderr)

    results = []
    nr_tasks = 0
    for f in files:
        for obj in read_json_objects(f):
            if obj.get("type") != "task":
                continue
            nr_tasks += 1
            results.extend(results_of_task(obj))

    #Warn about benchmarks that were run more than once with the same config
    seen = Counter((r.get("benchmark_path"), r.get("config")) for r in results)
    duplicates = [k for k, n in seen.items() if n > 1]
    if duplicates:
        print(f"Warning: {len(duplicates)} benchmark/config pairs occur more than once, e.g. {duplicates[0]}",
              file=sys.stderr)
    return results, nr_tasks


def fmt_time(times):
    if not times:
        return "-"
    return f"total {sum(times):.1f}s, median {statistics.median(times):.2f}s, max {max(times):.2f}s"


def print_summary(results, nr_tasks):
    print(f"Read {nr_tasks} tasks with {len(results)} results\n")
    groups = defaultdict(list)
    for r in results:
        groups[(r.get("library_name", "N/A"), r.get("config"))].append(r)

    for (library, config), rs in sorted(groups.items()):
        solving = Counter(r["solving"].get("status") for r in rs)
        checking = Counter(r["checking"].get("status") for r in rs)
        checked = [r for r in rs if r["checking"].get("status") not in ("skipped", "missing", "no_heap")]
        success = [r for r in checked if r["checking"].get("status") == "success"]

        print(f"=== {library} / {config}: {len(rs)} benchmarks")
        print("  solving:  " + ", ".join(f"{s} {n}" for s, n in solving.most_common()))
        print("  checking: " + ", ".join(f"{s} {n}" for s, n in checking.most_common()))
        if checked:
            print(f"  reconstructed {len(success)}/{len(checked)} checked proofs "
                  f"({100 * len(success) / len(checked):.1f}%)")
        print("  solving time (unsat):     " +
              fmt_time([r["solving"]["time_s"] for r in rs if r["solving"].get("status") == "unsat"]))
        print("  checking time (success):  " + fmt_time([r["checking"]["time_s"] for r in success]))

        rules = Counter(r["checking"]["error_rule"] for r in checked if "error_rule" in r["checking"])
        if rules:
            print("  failing rules: " + ", ".join(f"{rule} {n}" for rule, n in rules.most_common(10)))
        print()


def write_csv(results, path):
    fields = ["library_name", "config", "relative_benchmark_path", "benchmark_path",
              "solving_status", "solving_outcome", "solving_time_s", "nr_of_lines",
              "checking_status", "checking_outcome", "checking_time_s", "error_rule", "error_msg",
              "host", "walltime_s", "memory_mb"]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            s, c, j = r.get("solving", {}), r.get("checking", {}), r.get("job", {})
            writer.writerow({
                "library_name": r.get("library_name"), "config": r.get("config"),
                "relative_benchmark_path": r.get("relative_benchmark_path"),
                "benchmark_path": r.get("benchmark_path"),
                "solving_status": s.get("status"), "solving_outcome": s.get("outcome"),
                "solving_time_s": s.get("time_s"), "nr_of_lines": s.get("nr_of_lines"),
                "checking_status": c.get("status"), "checking_outcome": c.get("outcome"),
                "checking_time_s": c.get("time_s"), "error_rule": c.get("error_rule"),
                "error_msg": c.get("error_msg"),
                "host": j.get("host"), "walltime_s": j.get("walltime_s"), "memory_mb": j.get("memory_mb"),
            })


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="+", help="results directories or files")
    parser.add_argument("-o", "--output", help="write all results as one JSON array to this file")
    parser.add_argument("--csv", help="write all results as CSV to this file")
    args = parser.parse_args()

    results, nr_tasks = collect(args.inputs)
    if nr_tasks == 0:
        print("No task records found", file=sys.stderr)
        sys.exit(1)

    print_summary(results, nr_tasks)
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=1)
        print(f"Wrote {args.output}")
    if args.csv:
        write_csv(results, args.csv)
        print(f"Wrote {args.csv}")


if __name__ == "__main__":
    main()
