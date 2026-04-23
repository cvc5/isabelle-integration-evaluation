#!/usr/bin/env python3

import argparse
import json
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description="Merge a log JSON and a files JSON by matching (session, theory, base). "
                    "The two input files may be given in either order. "
                    "Warns about unmatched entries in either file."
    )
    parser.add_argument("input_a", help="Path to one of the input JSON files (log or files)")
    parser.add_argument("input_b", help="Path to the other input JSON file")
    parser.add_argument("output_json", help="Path to the merged JSON file to write")
    return parser.parse_args()


def looks_like_files_json(entries):
    for entry in entries:
        if isinstance(entry, dict) and "relative_path" in entry:
            return True
    return False


def looks_like_log_json(entries):
    for entry in entries:
        if isinstance(entry, dict) and "line" in entry and "outcome" in entry:
            return True
    return False


def load_inputs(path_a, path_b):
    with open(path_a) as f:
        data_a = json.load(f)
    with open(path_b) as f:
        data_b = json.load(f)

    a_is_files = looks_like_files_json(data_a)
    b_is_files = looks_like_files_json(data_b)
    a_is_log = looks_like_log_json(data_a)
    b_is_log = looks_like_log_json(data_b)

    if a_is_log and b_is_files:
        return data_a, data_b
    if b_is_log and a_is_files:
        return data_b, data_a
    raise SystemExit(
        "Error: could not distinguish log JSON from files JSON. "
        "One input must contain entries with 'relative_path' (files JSON) "
        "and the other with 'line' + 'outcome' (log JSON)."
    )


def _strategy_key(value):
    if value is None or value == "default":
        return None
    return value


def merge_calls(log_calls, files_calls):
    files_by_key = {}
    for call in files_calls:
        key = (call.get("solver"), _strategy_key(call.get("strategy")))
        files_by_key.setdefault(key, []).append(call)

    merged = []
    consumed = set()
    for log_call in log_calls:
        key = (log_call.get("solver"), _strategy_key(log_call.get("strategy")))
        bucket = files_by_key.get(key)
        if bucket:
            files_call = bucket.pop(0)
            consumed.add(id(files_call))
            merged.append({**log_call, **files_call})
        else:
            merged.append(log_call)
    for call in files_calls:
        if id(call) not in consumed:
            merged.append(call)
    return merged


def main():
    args = parse_args()

    log_entries, files_entries = load_inputs(args.input_a, args.input_b)

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
            files_entry = files_by_key[key]
            combined = {**log_entry, **files_entry}
            log_calls = log_entry.get("calls") or []
            files_calls = files_entry.get("calls") or []
            if log_calls or files_calls:
                combined["calls"] = merge_calls(log_calls, files_calls)
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
    output_path = Path(args.output_json)
    if output_path.exists():
        output_path.unlink()
    output_path.write_text(json.dumps(merged, indent=2) + "\n")
    print(f"Written {len(merged)} entries to {args.output_json}")
    print(f"  {len(matched_keys)} matched, "
          f"{len(log_entries) - len(matched_keys)} log-only, "
          f"{len(files_by_key) - len(matched_keys)} files-only")


if __name__ == "__main__":
    main()
