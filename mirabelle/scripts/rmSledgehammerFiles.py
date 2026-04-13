#!/usr/bin/env python3
import argparse
import json
import os
import sys


def count_assertions(path):
    try:
        with open(path, "r") as f:
            return sum(line.count("(assert ") for line in f)
    except OSError:
        return float("inf")


def count_lines(path):
    try:
        with open(path, "r") as f:
            return sum(1 for _ in f)
    except OSError:
        return None


def delete_call_files(call, dry_run, stats):
    for key in ("proof_path", "problem_path"):
        path = call.get(key)
        if not path:
            continue
        if dry_run:
            print(f"[dry-run] would delete: {path}")
            continue
        try:
            os.remove(path)
            stats["deleted"] += 1
        except FileNotFoundError:
            stats["missing"] += 1
        except OSError as e:
            print(f"error deleting {path}: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Remove sat/unknown sledgehammer call entries and delete their files."
    )
    parser.add_argument("input", help="Input JSON file (e.g., 'test').")
    parser.add_argument("output", help="Output JSON file.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be deleted without deleting.",
    )
    args = parser.parse_args()

    with open(args.input, "r") as f:
        data = json.load(f)

    stats = {"deleted": 0, "missing": 0}
    removed_outcome = 0
    removed_dedup = 0

    for entry in data:
        calls = entry.get("calls", [])
        surviving = []
        for call in calls:
            if call.get("prover_outcome") in ("sat", "unknown"):
                removed_outcome += 1
                delete_call_files(call, args.dry_run, stats)
            else:
                surviving.append(call)

        for call in surviving:
            call["nr_of_asserts"] = count_assertions(call.get("problem_path", ""))
            call["proof_size"] = count_lines(call.get("proof_path", ""))

        by_solver = {}
        for call in surviving:
            by_solver.setdefault(call.get("solver"), []).append(call)

        kept = []
        for solver, group in by_solver.items():
            best = min(group, key=lambda c: c["nr_of_asserts"])
            for call in group:
                if call is best:
                    kept.append(call)
                else:
                    removed_dedup += 1
                    delete_call_files(call, args.dry_run, stats)
        entry["calls"] = kept

    with open(args.output, "w") as f:
        json.dump(data, f, indent=2)

    remaining_calls = sum(len(entry.get("calls", [])) for entry in data)
    remaining_files = remaining_calls * 2

    print(
        f"removed {removed_outcome} sat/unknown entries; "
        f"removed {removed_dedup} duplicate-solver entries; "
        f"deleted {stats['deleted']} files; {stats['missing']} already missing."
    )
    print(f"remaining: {remaining_calls} calls, {remaining_files} files.")


if __name__ == "__main__":
    main()
