#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Filter benchmark entries by checking_outcome."
    )
    parser.add_argument("input_file", help="Path to the JSON file")
    parser.add_argument(
        "-c", "--config", default=None,
        help="Solver config to filter on. If not given, checks all configs."
    )
    parser.add_argument(
        "-n", "--max-lines", type=int, default=None,
        help="Maximum nr_of_lines in solving entries (filters out entries exceeding this)."
    )
    parser.add_argument(
        "-f", "--output-file", default=None,
        help="Output JSON file path. If not given, prints to stdout."
    )
    parser.add_argument(
        "-o", "--output-dir", default=None,
        help="Directory to copy benchmark and proof files into. Must exist."
    )
    args = parser.parse_args()

    if args.output_dir and not os.path.isdir(args.output_dir):
        print(f"Error: output directory '{args.output_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(args.input_file, "r") as f:
        data = json.load(f)

    filtered = []
    for entry in data:
        checking = entry.get("checking") or []
        solving = entry.get("solving") or []

        if args.config is not None:
            relevant = [
                c for c in checking
                if c.get("solver_config", "").strip() == args.config.strip()
            ]
        else:
            relevant = checking

        # Skip if no relevant checking entries exist
        if not relevant:
            continue

        # Keep entry only if at least one relevant checking outcome is NOT 0
        if all(str(c.get("checking_outcome", "")).strip() == "0" for c in relevant):
            continue

        # Optionally filter by max nr_of_lines in solving
        if args.max_lines is not None:
            rel_solving = solving
            if args.config is not None:
                rel_solving = [
                    s for s in solving
                    if s.get("solver_config", "").strip() == args.config.strip()
                ]
            if any(s.get("nr_of_lines", 0) > args.max_lines for s in rel_solving):
                continue

        filtered.append(entry)

    # Copy benchmark and proof files if -o is given
    if args.output_dir:
        copied = 0
        for entry in filtered:
            benchmark_path = entry.get("benchmark_path")
            if benchmark_path and os.path.isfile(benchmark_path):
                shutil.copy2(benchmark_path, args.output_dir)
                copied += 1
            elif benchmark_path:
                print(f"Warning: benchmark file not found: {benchmark_path}", file=sys.stderr)

            solving = entry.get("solving") or []
            if args.config is not None:
                solving = [
                    s for s in solving
                    if s.get("solver_config", "").strip() == args.config.strip()
                ]
            for s in solving:
                proof_path = s.get("proof_path")
                if proof_path and os.path.isfile(proof_path):
                    shutil.copy2(proof_path, args.output_dir)
                    copied += 1
                elif proof_path:
                    print(f"Warning: proof file not found: {proof_path}", file=sys.stderr)

        print(f"Copied {copied} files to {args.output_dir}", file=sys.stderr)

    output = json.dumps(filtered, indent=2)
    if args.output_file:
        with open(args.output_file, "w") as f:
            f.write(output)
        print(f"Wrote {len(filtered)} entries (out of {len(data)}) to {args.output_file}", file=sys.stderr)
    else:
        print(output)
        print(f"\n# {len(filtered)} entries (out of {len(data)}) passed filters", file=sys.stderr)


if __name__ == "__main__":
    main()
