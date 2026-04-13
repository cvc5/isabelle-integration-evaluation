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


def main():
    args = parse_args()

    input_dir = Path(args.input_directory).resolve()
    if not input_dir.is_dir():
        raise SystemExit(f"Error: '{args.input_directory}' is not a directory.")

    # Group files by (directory, prefix, extension)
    # Track all originals so we can detect collisions
    groups = defaultdict(dict)
    seen = defaultdict(list)  # (folder, prefix, ext) -> [original paths]

    errors = False
    for path in input_dir.rglob("*__*.smt_*"):
        if not path.is_file():
            continue
        name = path.name
        prefix, rest = name.split("__", 1)
        ext = rest.split(".", 1)[1] if "." in rest else ""

        if ext not in ("smt_in", "smt_out"):
            continue

        collision_key = (path.parent, prefix, ext)
        seen[collision_key].append(path)

        if len(seen[collision_key]) > 1:
            print(
                f"ERROR: collision for {prefix}.{ext} in {path.parent}:",
                file=sys.stderr,
            )
            for p in seen[collision_key]:
                print(f"  {p}", file=sys.stderr)
            errors = True
            continue

        key = (path.parent, prefix)
        if ext == "smt_in":
            groups[key]["smt_in"] = path
        elif ext == "smt_out":
            groups[key]["smt_out"] = path

    if errors:
        raise SystemExit("Aborting due to collisions.")

    if not groups:
        print(f"Warning: no matching files found in '{args.input_directory}'.", file=sys.stderr)
        Path(args.output_json).write_text("[]\n")
        return

    entries = []
    for (folder, prefix), files in sorted(groups.items()):
        ref = files.get("smt_out") or files["smt_in"]
        rel = ref.relative_to(input_dir)
        parts = rel.parts

        session = parts[0] if len(parts) > 1 else ""
        theory_raw = parts[1] if len(parts) > 2 else ""
        theory = re.sub(r"^\d+_", "", theory_raw)

        entry = {
            "base": prefix,
            "session": session,
            "theory": theory,
            "original_problem_name": files["smt_in"].name if "smt_in" in files else "",
        }

        if "smt_out" in files:
            out = files["smt_out"]
            entry["original_proof_name"] = out.name
            entry["benchmark_path"] = str(out)
            entry["relative_path"] = str(out.relative_to(input_dir))
            with open(out) as f:
                entry["solver_outcome"] = f.readline().rstrip("\n")

        entries.append(entry)

    Path(args.output_json).write_text(json.dumps(entries, indent=2) + "\n")
    print(f"Written {len(entries)} entries to {args.output_json}")


if __name__ == "__main__":
    main()
