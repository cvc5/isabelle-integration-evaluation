#!/usr/bin/env python3

import argparse
import json
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description="Merge a log JSON and a files JSON by matching (session, theory, base). "
                    "Warns about unmatched entries in either file."
    )
    parser.add_argument("log_json", help="Path to the log entries JSON file")
    parser.add_argument("files_json", help="Path to the files entries JSON file")
    parser.add_argument("output_json", help="Path to the merged JSON file to write")
    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.log_json) as f:
        log_entries = json.load(f)
    with open(args.files_json) as f:
        files_entries = json.load(f)

    # Index files entries by (session, theory, base)
    files_by_key = {}
    for entry in files_entries:
        key = (entry.get("session", ""), entry.get("theory", ""), entry.get("base", ""))
        files_by_key[key] = entry

    merged = []
    matched_keys = set()

    for log_entry in log_entries:
        key = (log_entry.get("session", ""), log_entry.get("theory", ""), log_entry.get("base", ""))
        if key in files_by_key:
            combined = {**log_entry, **files_by_key[key]}
            merged.append(combined)
            matched_keys.add(key)
        else:
            outcome = log_entry.get("outcome", "")
            if outcome != "timeout":
                print(
                    f"Warning: no problem/proof files found for log entry {key[2]} "
                    f"(session={key[0]}, theory={key[1]}, outcome={outcome})",
                    file=sys.stderr,
                )
            merged.append(log_entry)

    for key, files_entry in files_by_key.items():
        if key not in matched_keys:
            print(
                f"Warning: problem/proof file found but no log entry {key[2]} "
                f"(session={key[0]}, theory={key[1]})",
                file=sys.stderr,
            )
            merged.append(files_entry)

    from pathlib import Path
    Path(args.output_json).write_text(json.dumps(merged, indent=2) + "\n")
    print(f"Written {len(merged)} entries to {args.output_json}")
    print(f"  {len(matched_keys)} matched, "
          f"{len(log_entries) - len(matched_keys)} log-only, "
          f"{len(files_by_key) - len(matched_keys)} files-only")


if __name__ == "__main__":
    main()
