#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the full mirabelle log/files evaluation pipeline."
    )
    parser.add_argument("input_dir", help="Directory containing mirabelle.log and/or 0.sledgehammer/")
    parser.add_argument("output_dir", help="Directory to write the resulting JSON files to")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    mirabelle_log = input_dir / "mirabelle.log"
    sledgehammer_dir = input_dir / "0.sledgehammer"

    log_json = output_dir / "mirabelle_log.json"
    files_json = output_dir / "mirabelle_files.json"
    files_filtered_json = output_dir / "mirabelle_files_filtered.json"
    out_json = output_dir / "out.json"

    have_log = mirabelle_log.is_file()
    have_files = sledgehammer_dir.is_dir()

    if have_log:
        run([
            str(SCRIPT_DIR / "evaluateMirabelleLog.sh"),
            str(mirabelle_log),
            str(log_json),
        ])

    if have_files:
        run([
            sys.executable,
            str(SCRIPT_DIR / "evaluateSledgehammerOutput.py"),
            str(sledgehammer_dir),
            str(files_json),
        ])
        run([
            sys.executable,
            str(SCRIPT_DIR / "rmSledgehammerFiles.py"),
            str(files_json),
            str(files_filtered_json),
        ])

    if have_log and have_files:
        run([
            sys.executable,
            str(SCRIPT_DIR / "mergeLogAndFiles.py"),
            str(log_json),
            str(files_filtered_json),
            str(out_json),
        ])
    elif have_log:
        shutil.copyfile(log_json, out_json)
    elif have_files:
        shutil.copyfile(files_filtered_json, out_json)
    else:
        print(f"Neither {mirabelle_log} nor {sledgehammer_dir} found", file=sys.stderr)
        return 1

    print(f"Wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
