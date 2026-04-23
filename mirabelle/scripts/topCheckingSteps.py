#!/usr/bin/env python3

from __future__ import annotations

import argparse
import collections
import json
import os
from pathlib import Path


def parse_spy_file(path: Path) -> list[tuple[str, int]]:
    steps: list[tuple[str, int]] = []
    for raw in path.read_text(errors="replace").splitlines():
        line = raw.strip().rstrip(",")
        if not line or ":" not in line:
            continue
        name, _, rest = line.partition(":")
        name = name.strip()
        if not name or name[0].isdigit():
            continue
        for tok in rest.split(","):
            tok = tok.strip()
            if not tok:
                continue
            try:
                steps.append((name, int(tok)))
            except ValueError:
                pass
    return steps


def main() -> int:
    parser = argparse.ArgumentParser(
        description="For each (solver, benchmark) in all.json, print the top N "
                    "most-expensive checking steps from the spy file."
    )
    parser.add_argument("input_json", help="Path to all.json")
    parser.add_argument("-n", "--top", type=int, default=10, help="How many steps to show (default: 10)")
    parser.add_argument("-d", "--detailed", action="store_true",
                        help="Also show per-benchmark top lists.")
    parser.add_argument("-z", "--zulip", action="store_true",
                        help="Emit the two aggregate tables as Markdown (for Zulip).")
    parser.add_argument("-r", "--rule",
                        help="Show the benchmarks where a single instance of RULE "
                             "took the longest to check (one row per (solver, benchmark)).")
    args = parser.parse_args()

    entries = json.loads(Path(args.input_json).read_text())

    all_steps_by_solver: dict[str, list[tuple[str, int]]] = collections.defaultdict(list)
    ratios_by_solver: dict[str, dict[str, list[float]]] = collections.defaultdict(
        lambda: collections.defaultdict(list)
    )
    rule_hits_by_solver: dict[str, list[tuple[int, str, str]]] = collections.defaultdict(list)

    for entry in entries:
        benchmark = entry.get("benchmark_path", "<unknown>")
        bench_label = os.path.basename(benchmark)
        for check in entry.get("checking", []):
            solver = check.get("solver_config", "<unknown>")
            spy = check.get("spy_file_path")
            if not spy:
                continue
            spy_path = Path(os.path.expanduser(spy))
            if not spy_path.is_file():
                if args.detailed:
                    print(f"# {solver}  {bench_label}  (spy file missing: {spy_path})")
                continue

            steps = parse_spy_file(spy_path)
            all_steps_by_solver[solver].extend(steps)

            if args.rule:
                rule_max = max((t for n, t in steps if n == args.rule), default=None)
                if rule_max is not None:
                    rule_hits_by_solver[solver].append((rule_max, benchmark, str(spy_path)))

            per_file_sum: dict[str, int] = collections.defaultdict(int)
            per_file_count: dict[str, int] = collections.defaultdict(int)
            for name, t in steps:
                per_file_sum[name] += t
                per_file_count[name] += 1
            file_total = sum(per_file_sum.values())
            if file_total <= 0:
                continue
            for name, total in per_file_sum.items():
                per_occurrence = total / per_file_count[name]
                ratios_by_solver[solver][name].append(per_occurrence / file_total)

            if args.detailed:
                if not steps:
                    print(f"# {solver}  {bench_label}  (no steps)")
                    continue
                top = sorted(steps, key=lambda s: s[1], reverse=True)[: args.top]
                print(f"# {solver}  {bench_label}")
                for name, t in top:
                    print(f"  {t:>15}  {name}")
                print()

    if args.detailed:
        print("=" * 60)

    if args.rule:
        for solver in sorted(rule_hits_by_solver):
            hits = sorted(rule_hits_by_solver[solver], key=lambda h: h[0], reverse=True)[: args.top]
            print(f"# {solver}  (top {len(hits)} benchmarks where one `{args.rule}` step took longest)")
            for t, bench, spy in hits:
                print(f"  {t:>15}")
                print(f"    problem: {bench}")
                print(f"    spy:     {spy}")
            if not hits:
                print(f"  (no instances of `{args.rule}` found)")
            print()
        return 0

    for solver in sorted(all_steps_by_solver):
        steps = all_steps_by_solver[solver]
        if not steps:
            continue
        totals: dict[str, int] = collections.defaultdict(int)
        for name, t in steps:
            totals[name] += t
        top = sorted(totals.items(), key=lambda s: s[1], reverse=True)[: args.top]

        ratio_stats: list[tuple[str, float, float, int]] = []
        for name, rs in ratios_by_solver.get(solver, {}).items():
            ratio_stats.append((name, sum(rs) / len(rs), max(rs), len(rs)))
        top_avg = sorted(ratio_stats, key=lambda s: s[1], reverse=True)[: args.top]
        top_max = sorted(ratio_stats, key=lambda s: s[2], reverse=True)[: args.top]

        if args.zulip:
            print(f"**{solver} — top {args.top} rules (summed across benchmarks)**\n")
            print("| Rule | Total time |")
            print("| --- | ---: |")
            for name, t in top:
                print(f"| `{name}` | {t} |")
            print()
            if top_avg:
                print(f"**{solver} — top {args.top} rules by avg per-occurrence share of file time**\n")
                print("| Rule | Avg share | Files |")
                print("| --- | ---: | ---: |")
                for name, avg, _mx, n in top_avg:
                    print(f"| `{name}` | {avg * 100:.2f}% | {n} |")
                print()
            if top_max:
                print(f"**{solver} — top {args.top} rules by max per-occurrence share of file time**\n")
                print("| Rule | Max share | Files |")
                print("| --- | ---: | ---: |")
                for name, _avg, mx, n in top_max:
                    print(f"| `{name}` | {mx * 100:.2f}% | {n} |")
                print()
        else:
            print(f"# {solver}  (top {args.top} rules, summed across all benchmarks)")
            for name, t in top:
                print(f"  {t:>15}  {name}")
            print()
            if top_avg:
                print(f"# {solver}  (top {args.top} rules by avg per-occurrence share of file time)")
                for name, avg, _mx, n in top_avg:
                    print(f"  {avg * 100:>7.2f}%  files={n:<4}  {name}")
                print()
            if top_max:
                print(f"# {solver}  (top {args.top} rules by max per-occurrence share of file time)")
                for name, _avg, mx, n in top_max:
                    print(f"  {mx * 100:>7.2f}%  files={n:<4}  {name}")
                print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
