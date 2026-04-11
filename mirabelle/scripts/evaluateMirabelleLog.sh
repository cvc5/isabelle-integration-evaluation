#!/usr/bin/env python3

from __future__ import annotations

import argparse
import collections
import dataclasses
import json
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Iterable


LOG_RE = re.compile(
    r"^\d+\.sledgehammer\s+goal\.[^\s]+\s+\d+ms\s+"
    r"(?P<theory>[A-Za-z0-9_.']+)\s+(?P<line>\d+):(?P<offset>\d+)\s+"
    r"(?P<outcome>some|timeout|none)\b"
)
SMT_BACKEND_RE = re.compile(r"Try this: (?:by|apply) \(smt \((?P<backend>[^)]*)\)")

@dataclasses.dataclass(frozen=True)
class ProblemRef:
    session: str
    theory: str
    base: str

@dataclasses.dataclass
class LogEntry:
    ref: ProblemRef
    outcome: str
    theory_long_name: str
    line_text: str
    suggested_backend: str | None

def relpath(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)

def theory_from_dir(dirname: str) -> str:
    return re.sub(r"^\d+_", "", dirname)

def parse_mirabelle_log(log_path: Path) -> list[LogEntry]:
    if not log_path.is_file():
        return []

    entries: list[LogEntry] = []
    for line in log_path.read_text(errors="replace").splitlines():
        match = LOG_RE.match(line)
        if match is None:
            continue
        theory_long_name = match.group("theory")
        session, _, theory = theory_long_name.rpartition(".")
        if not session:
            session = theory_long_name
        ref = ProblemRef(
            session=session,
            theory=theory,
            base=f"prob_{int(match.group('line')):05d}_{int(match.group('offset')):06d}",
        )
        backend_match = SMT_BACKEND_RE.search(line)
        backend = None
        if backend_match:
            backend_field = backend_match.group("backend").strip()
            backend = backend_field.split(",", 1)[0].strip()
        entries.append(
            LogEntry(
                ref=ref,
                outcome=match.group("outcome"),
                theory_long_name=theory_long_name,
                line_text=line,
                suggested_backend=backend,
            )
        )
    return entries


def default_isabelle_binary(repo_root: Path) -> Path | None:
    candidate = repo_root / "bin" / "isabelle"
    if candidate.is_file():
        return candidate
    return None


def isabelle_string(path: Path) -> str:
    return str(path).replace("\\", "\\\\").replace('"', '\\"')

def count_by(items: Iterable[str]) -> collections.Counter[str]:
    return collections.Counter(items)


def shorten(text: str, limit: int = 180) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."

def render_summary(
    log_entries: list[LogEntry],
) -> str:
    lines: list[str] = []

    lines.append("# output_mirabelle summary")
    lines.append("")

    if log_entries:
        outcome_counts = count_by(entry.outcome for entry in log_entries)
        backend_counts = count_by(
            entry.suggested_backend for entry in log_entries if entry.suggested_backend is not None
        )
        lines.append("## Mirabelle log")
        lines.append(f"- goals: {len(log_entries)}")
        lines.append(
            f"- outcomes: some={outcome_counts.get('some', 0)}, timeout={outcome_counts.get('timeout', 0)}, none={outcome_counts.get('none', 0)}"
        )
        if backend_counts:
            backend_text = ", ".join(
                f"{backend}={count}" for backend, count in backend_counts.most_common()
            )
            lines.append(f"- suggested SMT backends: {backend_text}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"

def json_payload(log_entries: list[LogEntry]) -> dict:
    return {
        "log_entries": [
            {
                "session": entry.ref.session,
                "theory": entry.ref.theory,
                "base": entry.ref.base,
                "outcome": entry.outcome,
                "theory_long_name": entry.theory_long_name,
                "suggested_backend": entry.suggested_backend,
                "line_text": entry.line_text,
            }
            for entry in log_entries
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transform mirabelle.log into .json file."
    )
    parser.add_argument(
        "--mirabelle-log",
        help="path to mirabelle.log",
    )
    parser.add_argument(
        "--json",
        default=None,
        help="optional path for machine-readable JSON output",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
     
    log_entries = parse_mirabelle_log(Path(args.mirabelle_log))

    summary = render_summary(
        log_entries=log_entries,
    )
    sys.stdout.write(summary)

    if args.json:
        json_path = Path(args.json)
        json_path.write_text(
            json.dumps(json_payload(log_entries), indent=2, sort_keys=True),
            encoding="utf-8",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

