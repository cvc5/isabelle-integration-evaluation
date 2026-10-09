#!/usr/bin/env python3
"""Collect the results of solveAndCheckWrapper.sh runs and print a summary.

Reads all task records written by submit-job (files containing JSON objects with "type": "task",
either one object per file, one per line, or a JSON array) below the given directories. Every
"RESULT_JSON: {...}" line in a task's output_log becomes one result. Configs that were requested
with -c but have no result (crash, slurm timeout, missing binary, ...) are added with status "missing".
Each result also gets a run status: "finished" if it has a result, "memout" if benchexec killed the task
for exceeding its memory limit while this config was running (solving and checking are then "interrupted",
as it is not known which of them ran out of memory), "not_run" for the configs after it and "missing" otherwise.

At the end it asks whether to save the benchmarks each config solved (unsat) to prev_solved_<config>.txt
in the benchmark input directory. solveAndCheckWrapper.sh then offers to run only on those.

With --copy-failed DIR, the problems whose proof was checked by Isabelle but not reconstructed
successfully are copied to DIR/<config>/<relative benchmark path>, together with a DIR/<config>/failures.csv
listing status and error of each.

If a directory is given and it contains a results.json, only that file is read. Otherwise all results.json.gz
and results_<config>.json.gz files below it (written by submit-job) are decompressed with gunzip, merged and
saved as results.json in the directory, so later runs read that directly. Without any of these, all files
below the directory are read.

Usage: evaluate.py [-o combined.json] [--csv results.csv] [--copy-failed DIR] <results dir or file>...
"""

import argparse
import csv
import json
import re
import shutil
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

RESULT_PREFIX = "RESULT_JSON: "
SEPARATOR = "-" * 80
#Checking statuses meaning that Isabelle did not check a proof
NOT_CHECKED = ("skipped", "missing", "no_heap", "interrupted", "not_run")


def read_json_objects(path):
    """Yield all JSON objects in a file (single object, JSON array, or JSON lines)."""
    try:
        text = path.read_text(errors="replace")
    except OSError as e:
        print(f"Warning: cannot read {path}: {e}", file=sys.stderr)
        return
    yield from parse_json_objects(text)


def parse_json_objects(text):
    """Yield all JSON objects in a string (single object, JSON array, or JSON lines)."""
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
            elif key == "terminationreason":
                info["terminationreason"] = value.strip()
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
        r["run"] = {"status": "finished"}
        r["job"] = job
        if other_lines:
            r["job_messages"] = other_lines

    #Add configs without a result. If benchexec killed the task for exceeding its memory limit, the whole
    #task died and solveAndCheck.sh could not write a result. Configs run in the order given with -c, so the
    #first config without a result is the one that ran out of memory, the following ones did not run.
    found = {r.get("config") for r in results}
    killed = run_info.get("terminationreason") == "memory"
    run_status = "memout" if killed else "missing"
    benchmark_path = task.get("job_args", "").strip()
    #The last two arguments of solveAndCheck.sh are base_dir and the benchmark
    args = command.split()
    base_dir = args[-2].rstrip("/") + "/" if len(args) >= 2 else ""
    relative_path = benchmark_path[len(base_dir):] if benchmark_path.startswith(base_dir) else benchmark_path
    for config in requested_configs(command):
        if config not in found:
            status = {"memout": "interrupted", "not_run": "not_run"}.get(run_status, "missing")
            results.append({
                "benchmark_name": Path(benchmark_path).stem,
                "benchmark_path": benchmark_path,
                "relative_benchmark_path": relative_path,
                "library_name": (re.search(r"(?:^|\s)-l\s+(\S+)", command) or [None, "N/A"])[1],
                "config": config,
                "run": {"status": run_status},
                "solving": {"status": status},
                "checking": {"status": status},
                "job": job,
                "job_messages": other_lines,
            })
            if killed:
                run_status = "not_run"
    return results


def gunzip_results(directory):
    """Decompress all results.json.gz and results_<config>.json.gz files below directory and merge them into
    directory/results.json. Return the path of that file or None if there are no such files."""
    archives = sorted(f for f in directory.rglob("results*.json.gz")
                      if f.is_file() and re.fullmatch(r"results(_.+)?\.json\.gz", f.name))
    if not archives:
        return None
    objects = []
    for archive in archives:
        proc = subprocess.run(["gunzip", "-c", str(archive)], capture_output=True, text=True, errors="replace")
        if proc.returncode != 0:
            print(f"Warning: cannot gunzip {archive}: {proc.stderr.strip()}", file=sys.stderr)
            continue
        objects.extend(parse_json_objects(proc.stdout))
    out = directory / "results.json"
    with open(out, "w") as f:
        json.dump(objects, f)
    print(f"Merged {len(archives)} file(s) into {out}: " + ", ".join(str(a) for a in archives), file=sys.stderr)
    return out


def collect(paths):
    files = []
    for p in map(Path, paths):
        if p.is_dir():
            if (p / "results.json").is_file():
                files.append(p / "results.json")
            elif (merged := gunzip_results(p)) is not None:
                files.append(merged)
            else:
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
        run = Counter(r.get("run", {}).get("status") for r in rs)
        solving = Counter(r["solving"].get("status") for r in rs)
        checking = Counter(r["checking"].get("status") for r in rs)
        checked = [r for r in rs if r["checking"].get("status") not in NOT_CHECKED]
        success = [r for r in checked if r["checking"].get("status") == "success"]

        print(f"=== {library} / {config}: {len(rs)} benchmarks")
        print("  run:      " + ", ".join(f"{s} {n}" for s, n in run.most_common()))
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


def save_solved(results):
    """Write prev_solved_<config>.txt with the benchmarks each config solved (unsat) into the input directory,
    where solveAndCheckWrapper.sh picks them up."""
    #(input directory, config) -> solved benchmarks. The input directory is the benchmark path without
    #the path relative to it
    solved = defaultdict(set)
    for r in results:
        path, rel = r.get("benchmark_path", ""), r.get("relative_benchmark_path") or ""
        if not rel or not path.endswith(rel):
            continue
        input_dir = path[:-len(rel)].rstrip("/")
        solved[(input_dir, r.get("config"))]
        if r["solving"].get("status") == "unsat":
            solved[(input_dir, r.get("config"))].add(path)

    for (input_dir, config), paths in sorted(solved.items()):
        out = Path(input_dir) / f"prev_solved_{config}.txt"
        try:
            out.write_text("".join(p + "\n" for p in sorted(paths)))
            print(f"Wrote {out} with {len(paths)} benchmarks")
        except OSError as e:
            print(f"Error: cannot write {out}: {e}", file=sys.stderr)


def copy_failed(results, out_dir):
    """Copy the problems whose proof Isabelle checked without success to out_dir/<config>/."""
    failed = defaultdict(list)
    for r in results:
        status = r["checking"].get("status")
        if status not in NOT_CHECKED and status != "success":
            failed[r.get("config")].append(r)

    for config, rs in sorted(failed.items()):
        config_dir = Path(out_dir) / config
        config_dir.mkdir(parents=True, exist_ok=True)
        copied = 0
        with open(config_dir / "failures.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["relative_benchmark_path", "status", "outcome", "error_rule", "error_msg", "benchmark_path"])
            for r in sorted(rs, key=lambda r: r.get("relative_benchmark_path") or r.get("benchmark_path")):
                c = r["checking"]
                rel = r.get("relative_benchmark_path") or Path(r["benchmark_path"]).name
                writer.writerow([rel, c.get("status"), c.get("outcome"), c.get("error_rule"), c.get("error_msg"),
                                 r["benchmark_path"]])
                target = config_dir / rel
                try:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(r["benchmark_path"], target)
                    copied += 1
                except OSError as e:
                    print(f"Warning: cannot copy {r['benchmark_path']}: {e}", file=sys.stderr)
        print(f"Copied {copied} of {len(rs)} failed problems of {config} to {config_dir}")


def ask(question):
    try:
        return input(question).strip().lower() in ("y", "yes")
    except EOFError:
        return False


def write_csv(results, path):
    fields = ["library_name", "config", "relative_benchmark_path", "benchmark_path", "run_status",
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
                "benchmark_path": r.get("benchmark_path"), "run_status": r.get("run", {}).get("status"),
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
    parser.add_argument("--copy-failed", metavar="DIR",
                        help="copy the problems whose proof was checked with an error to DIR/<config>/")
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
    if args.copy_failed:
        copy_failed(results, args.copy_failed)

    if ask("Save the benchmarks each solver solved (unsat) to prev_solved_<config>.txt in the input directory? [y/N] "):
        save_solved(results)


if __name__ == "__main__":
    main()
