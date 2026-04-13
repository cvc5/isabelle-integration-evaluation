#!/usr/bin/env python3

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scan a directory recursively for .smt_in/.smt_out file pairs "
                    "and produce a JSON file grouping them by common prefix."
    )
    parser.add_argument("input_directory", help="Directory to scan recursively")
    parser.add_argument("output_json", help="Path to the JSON file to write")
    return parser.parse_args()


def parse_filename(name):
    """Parse prob_AAAAA_BBBBBB__CCCCCCCC_DDDDDDDD.smt_in/out"""
    m = re.match(r'^(prob_(\d+)_(\d+))__(\d+)_(\d+)\.(smt_(?:in|out))$', name)
    if not m:
        return None
    return {
        "base": m.group(1),
        "part1": m.group(2),
        "part2": m.group(3),
        "part3": m.group(4),
        "part4": m.group(5),
        "ext": m.group(6),
    }


CVC5_STRATEGIES = {
    "best": [],
    "trigger_last": ["--full-saturate-quant", "--inst-when=full-last-call", "--inst-no-entail",
                     "--term-db-mode=relevant", "--multi-trigger-linear"],
    "quant_saturate": ["--decision=internal", "--simplification=none", "--full-saturate-quant"],
    "trigger_max": ["--trigger-sel=max", "--full-saturate-quant"],
    "trigger_relev": ["--relevant-triggers", "--full-saturate-quant"],
    "term_relev": ["--term-db-mode=relevant", "--full-saturate-quant"],
    "noematch": ["--no-e-matching", "--full-saturate-quant"],
    "fmf": ["--finite-model-find", "--decision=internal"],
}

VERIT_STRATEGIES = {
    "default": [],
    "best": ["--index-sorts", "--index-fresh-sorts", "--triggers-new",
             "--triggers-sel-rm-specific"],
    "del_insts": ["--index-sorts", "--index-fresh-sorts", "--ccfv-breadth",
                  "--inst-deletion", "--index-SAT-triggers", "--inst-deletion-loops",
                  "--inst-deletion-track-vars", "--inst-deletion", "--index-SAT-triggers"],
    "ccfv_SIG": ["--index-SIG", "--triggers-new", "--triggers-sel-rm-specific"],
    "ccfv_threshold": ["--index-sorts", "--index-fresh-sorts", "--triggers-new",
                       "--triggers-sel-rm-specific", "--triggers-restrict-combine",
                       "--inst-deletion", "--index-SAT-triggers", "--inst-deletion-loops",
                       "--inst-deletion-track-vars", "--inst-deletion", "--index-SAT-triggers",
                       "--inst-sorts-threshold=100000", "--ematch-exp=10000000",
                       "--ccfv-index=100000", "--ccfv-index-full=1000"],
}

Z3_STRATEGIES = {
    "default": [],
}

CVC5_COMMON_PREFIXES = [
    "--no-stats", "--sat-random-seed=", "--lang=", "--proof-prune",
    "--proof-prune-input", "--proof-elim-subtypes",
    "--proof-alethe-define-skolems", "--proof-format-mode=", "--tlimit",
    "--proof-granularity=", "--full-saturate-quant", "--proof-mode=",
]

VERIT_COMMON_PREFIXES = [
    "--proof-define-skolems", "--proof-prune", "--proof-merge",
    "--print-cvc5-numbers", "--disable-print-success", "--disable-banner", "--tlimit",
    "--proof-with-sharing",
]

Z3_COMMON_PREFIXES = [
    "smt.random_seed=", "smt.refine_inj_axioms=", "-smt2", "-T:",
]


def is_common_option(opt, prefixes):
    for prefix in prefixes:
        if opt == prefix or opt.startswith(prefix):
            return True
    return False


def identify_solver_strategy(first_line):
    """Given the first line of an smt_in file, return (solver, strategy)."""
    line = first_line.lstrip("; ").strip()
    opts = line.split()

    # Remove bare values that follow space-separated options like --tlimit 5000 or -T: 30
    filtered_opts = []
    skip_next = False
    for o in opts:
        if skip_next:
            skip_next = False
            continue
        if o in ("--tlimit", "-T:"):
            skip_next = True
            filtered_opts.append(o)
            continue
        filtered_opts.append(o)
    opts = filtered_opts

    has_cvc5_marker = any(
        is_common_option(o, ["--proof-alethe-define-skolems", "--proof-elim-subtypes",
                             "--proof-format-mode=", "--proof-prune-input",
                             "--proof-granularity=", "--proof-mode="])
        for o in opts
    )
    has_verit_marker = any(
        is_common_option(o, ["--proof-define-skolems", "--proof-merge",
                             "--print-cvc5-numbers", "--disable-print-success",
                             "--disable-banner", "--proof-with-sharing"])
        for o in opts
    )
    has_z3_marker = any(
        is_common_option(o, ["smt.random_seed=", "smt.refine_inj_axioms=", "-smt2"])
        for o in opts
    )

    if has_z3_marker and not has_cvc5_marker and not has_verit_marker:
        solver = "z3"
        strategies = Z3_STRATEGIES
        common_prefixes = Z3_COMMON_PREFIXES
    elif has_cvc5_marker and not has_verit_marker and not has_z3_marker:
        solver = "cvc5"
        strategies = CVC5_STRATEGIES
        common_prefixes = CVC5_COMMON_PREFIXES
    elif has_verit_marker and not has_cvc5_marker and not has_z3_marker:
        solver = "verit"
        strategies = VERIT_STRATEGIES
        common_prefixes = VERIT_COMMON_PREFIXES
    else:
        return "unknown", "unknown"

    extra_opts = set(o for o in opts if not is_common_option(o, common_prefixes))

    for name, stgy_opts in strategies.items():
        stgy_extra = set(o for o in stgy_opts if not is_common_option(o, common_prefixes))
        if stgy_extra == extra_opts:
            return solver, name

    return solver, f"unknown({' '.join(sorted(extra_opts))})"


def main():
    args = parse_args()

    input_dir = Path(args.input_directory).resolve()
    if not input_dir.is_dir():
        raise SystemExit(f"Error: '{args.input_directory}' is not a directory.")

    seen = defaultdict(list)
    groups = defaultdict(list)

    errors = False
    for path in sorted(input_dir.rglob("*.smt_*")):
        if not path.is_file():
            continue
        parsed = parse_filename(path.name)
        if not parsed:
            continue

        collision_key = (path.parent, parsed["part1"], parsed["part2"], parsed["part4"], parsed["ext"])
        seen[collision_key].append(path)
        if len(seen[collision_key]) > 1:
            print(
                f"ERROR: collision for parts ({parsed['part1']}, {parsed['part2']}, *, {parsed['part4']}).{parsed['ext']} in {path.parent}:",
                file=sys.stderr,
            )
            for p in seen[collision_key]:
                print(f"  {p}", file=sys.stderr)
            errors = True
            continue

        group_key = (path.parent, parsed["base"])
        groups[group_key].append((path, parsed))

    if errors:
        raise SystemExit("Aborting due to collisions.")

    if not groups:
        print(f"Warning: no matching files found in '{args.input_directory}'.", file=sys.stderr)
        Path(args.output_json).write_text("[]\n")
        return

    entries = []
    for (folder, base), file_list in sorted(groups.items()):
        ref = file_list[0][0]
        rel_dir = ref.parent.relative_to(input_dir)

        parts = rel_dir.parts
        session = parts[0] if len(parts) > 0 else ""
        theory_raw = parts[1] if len(parts) > 1 else ""
        theory = re.sub(r"^\d+_", "", theory_raw)

        problems = defaultdict(list)
        proofs = defaultdict(list)

        for path, parsed in file_list:
            match_key = (parsed["part1"], parsed["part2"], parsed["part4"])
            if parsed["ext"] == "smt_in":
                problems[match_key].append((path, parsed))
            else:
                proofs[match_key].append((path, parsed))

        for mk, items in problems.items():
            if len(items) > 1:
                print(
                    f"Warning: {len(items)} problems match key {mk} in {folder}:",
                    file=sys.stderr,
                )
                for p, _ in items:
                    print(f"  {p}", file=sys.stderr)
        for mk, items in proofs.items():
            if len(items) > 1:
                print(
                    f"Warning: {len(items)} proofs match key {mk} in {folder}:",
                    file=sys.stderr,
                )
                for p, _ in items:
                    print(f"  {p}", file=sys.stderr)

        all_match_keys = set(problems.keys()) | set(proofs.keys())
        calls = []

        for mk in sorted(all_match_keys):
            call = {}

            prob_list = problems.get(mk, [])
            if prob_list:
                p, parsed = prob_list[0]
                call["original_problem_name"] = p.name
                call["problem_path"] = str(p)

                with open(p) as fh:
                    first_line = fh.readline().rstrip("\n")
                solver, strategy = identify_solver_strategy(first_line)
                call["solver"] = solver
                call["strategy"] = strategy

            proof_list = proofs.get(mk, [])
            if proof_list:
                p, parsed = proof_list[0]
                call["original_proof_name"] = p.name
                call["proof_path"] = str(p)
                with open(p) as fh:
                    call["prover_outcome"] = fh.readline().rstrip("\n")

            calls.append(call)

        entry = {
            "base": base,
            "session": session,
            "theory": theory,
            "relative_path": str(rel_dir),
            "calls": calls,
        }
        entries.append(entry)

    Path(args.output_json).write_text(json.dumps(entries, indent=2) + "\n")
    print(f"Written {len(entries)} entries to {args.output_json}")


if __name__ == "__main__":
    main()
