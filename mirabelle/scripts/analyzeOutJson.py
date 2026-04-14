#!/usr/bin/env python3

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize a merged out.json: suggested backends, unsat counts, "
                    "and average proof size per solver."
    )
    parser.add_argument("input_json", help="Path to out.json (merged log + files)")
    args = parser.parse_args()

    entries = json.loads(Path(args.input_json).read_text())

    backend_counts: collections.Counter[str] = collections.Counter()
    unsat_entries_by_solver: collections.Counter[str] = collections.Counter()
    proof_sizes_by_solver: dict[str, list[int]] = collections.defaultdict(list)
    proof_size_field_by_solver: dict[str, list[float]] = collections.defaultdict(list)

    for entry in entries:
        backend = entry.get("suggested_backend")
        if backend:
            backend_counts[backend] += 1

        calls = entry.get("calls") or []

        solvers_with_unsat = set()
        for call in calls:
            solver = call.get("solver") or "unknown"
            if call.get("prover_outcome") == "unsat":
                solvers_with_unsat.add(solver)
                proof_path = call.get("proof_path")
                if proof_path:
                    p = Path(proof_path)
                    if p.is_file():
                        proof_sizes_by_solver[solver].append(p.stat().st_size)
                proof_size_field = call.get("proof_size")
                if isinstance(proof_size_field, (int, float)):
                    proof_size_field_by_solver[solver].append(proof_size_field)
        for solver in solvers_with_unsat:
            unsat_entries_by_solver[solver] += 1

    print("# Suggested SMT backends")
    if backend_counts:
        for backend, count in backend_counts.most_common():
            print(f"  {backend}: {count}")
    else:
        print("  (none)")
    print()

    print("# Entries with an unsat call, by solver")
    if unsat_entries_by_solver:
        for solver, count in unsat_entries_by_solver.most_common():
            print(f"  {solver}: {count}")
    else:
        print("  (none)")
    print()

    print("# Average proof size per solver")
    all_solvers = sorted(set(proof_sizes_by_solver) | set(proof_size_field_by_solver))
    if all_solvers:
        for solver in all_solvers:
            sizes = proof_sizes_by_solver.get(solver, [])
            field = proof_size_field_by_solver.get(solver, [])
            parts = []
            if sizes:
                parts.append(f"{sum(sizes) / len(sizes):.1f} bytes")
            if field:
                parts.append(f"line nr avg={sum(field) / len(field):.1f}")
            n = len(sizes) if sizes else len(field)
            print(f"  {solver}: {', '.join(parts)} (n={n})")
    else:
        print("  (none)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
