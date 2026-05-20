#!/usr/bin/env python3

from __future__ import annotations

import argparse
import collections
import dataclasses
import json
import re
import sys
from pathlib import Path
from typing import Iterable


LOG_RE = re.compile(
    r"^\d+\.sledgehammer\s+goal\.[^\s]+\s+\d+ms\s+"
    r"(?P<theory>[A-Za-z0-9_.'-]+)\s+(?P<line>\d+):(?P<offset>\d+)\s+"
    r"(?P<outcome>some|timeout|none)\b"
)
SMT_BACKEND_RE = re.compile(
    r"(?:Try this: (?:by|apply)|Preplay:) \(smt \((?P<backend>[^)]*)\)"
)
SH_TIME_RE = re.compile(r"\(SH\s+(?P<sh>\d+)ms")
ATP_TIME_RE = re.compile(r"ATP\s+(?P<atp>\d+)ms")
PREPLAY_CMD_RE = re.compile(
    r"(?:Try this:|Preplay:)\s+(?P<cmd>.+?)"
    r"(?:\s+\((?:>?\s*\d+[\d.]*\s*(?:ms|s)\b[^)]*|failed)\)\s*)?$"
)
PREPLAY_TIME_RE = re.compile(
    r"\(>?\s*(?P<time>\d+[\d.]*)\s*(?P<unit>ms|s)(?:,\s*timed out)?\)\s*$"
)
PREPLAY_TIMED_OUT_RE = re.compile(r"timed out\)\s*$")


@dataclasses.dataclass(frozen=True)
class ProblemRef:
    session: str
    theory: str
    base: str


@dataclasses.dataclass
class PreplayCall:
    solver: str | None
    strategy: str | None
    preplay_command: str | None
    preplay_time: int | None
    outcome: str


@dataclasses.dataclass
class LogEntry:
    ref: ProblemRef
    line: int
    outcome: str
    suggested_backend: str | None
    strategy: str | None
    sledgehammer_time: int | None
    atp_time: int | None
    preplay_command: str | None
    preplay_time: int | None
    calls: list[PreplayCall] = dataclasses.field(default_factory=list)


def parse_mirabelle_log(log_path: Path) -> list[LogEntry]:
    if not log_path.exists():
        raise FileNotFoundError(f"log file does not exist: {log_path}")
    if not log_path.is_file():
        raise IsADirectoryError(
            f"log path is not a regular file (is it a directory?): {log_path}"
        )

    try:
        raw_text = log_path.read_text(errors="replace")
    except OSError as exc:
        raise OSError(f"could not read log file {log_path}: {exc}") from exc

    all_lines = raw_text.splitlines()
    if not all_lines:
        print(
            f"warning: log file is empty: {log_path}",
            file=sys.stderr,
        )

    entries: list[LogEntry] = []
    matched_lines = 0
    for line in all_lines:
        match = LOG_RE.match(line)
        if match is None:
            continue
        matched_lines += 1
        theory_long_name = match.group("theory")
        session, _, theory = theory_long_name.rpartition(".")
        if not session:
            session = theory_long_name
        ref = ProblemRef(
            session=session,
            theory=theory,
            base=f"prob_{int(match.group('line')):05d}_{int(match.group('offset')):06d}",
        )
        line_number = int(match.group("line"))
        raw_outcome = match.group("outcome")

        sh_match = SH_TIME_RE.search(line)
        atp_match = ATP_TIME_RE.search(line)

        is_preplay_continuation = (
            raw_outcome == "some"
            and sh_match is None
            and atp_match is None
            and "Preplay:" in line
        )
        if is_preplay_continuation:
            if entries and entries[-1].ref == ref and entries[-1].line == line_number:
                cmd_match = PREPLAY_CMD_RE.search(line)
                cmd = cmd_match.group("cmd").strip() if cmd_match else None
                backend_match = SMT_BACKEND_RE.search(line)
                call_solver = None
                call_strategy = None
                if backend_match:
                    parts = [p.strip() for p in backend_match.group("backend").split(",")]
                    call_solver = parts[0]
                    if len(parts) > 1:
                        call_strategy = parts[1]
                call_time = None
                time_match = PREPLAY_TIME_RE.search(line)
                if time_match:
                    t = float(time_match.group("time"))
                    if time_match.group("unit") == "s":
                        t *= 1000
                    call_time = int(t)
                if line.rstrip().endswith("(failed)"):
                    call_outcome = "failed"
                elif PREPLAY_TIMED_OUT_RE.search(line):
                    call_outcome = "timed out"
                else:
                    call_outcome = "success"
                entries[-1].calls.append(
                    PreplayCall(
                        solver=call_solver,
                        strategy=call_strategy,
                        preplay_command=cmd,
                        preplay_time=call_time,
                        outcome=call_outcome,
                    )
                )
            continue

        backend_match = SMT_BACKEND_RE.search(line)
        backend = None
        strategy = None
        if backend_match:
            parts = [p.strip() for p in backend_match.group("backend").split(",")]
            backend = parts[0]
            if len(parts) > 1:
                strategy = parts[1]

        sh_time = int(sh_match.group("sh")) if sh_match else None
        atp_time = int(atp_match.group("atp")) if atp_match else None

        preplay_command = None
        preplay_time = None

        if raw_outcome == "some":
            if PREPLAY_TIMED_OUT_RE.search(line):
                outcome = "failure preplay"
            else:
                outcome = "success preplay"
            cmd_match = PREPLAY_CMD_RE.search(line)
            if cmd_match:
                preplay_command = cmd_match.group("cmd").strip()
            time_match = PREPLAY_TIME_RE.search(line)
            if time_match:
                t = float(time_match.group("time"))
                if time_match.group("unit") == "s":
                    t *= 1000
                preplay_time = int(t)
        else:
            if raw_outcome == "none":
                if "Prover error:" in line:
                    outcome = "prover error"
                else:
                    outcome = "other error"
            else:
                outcome = raw_outcome

        entries.append(
            LogEntry(
                ref=ref,
                line=line_number,
                outcome=outcome,
                suggested_backend=backend,
                strategy=strategy,
                sledgehammer_time=sh_time,
                atp_time=atp_time,
                preplay_command=preplay_command,
                preplay_time=preplay_time,
            )
        )

    if all_lines and matched_lines == 0:
        print(
            f"warning: none of the {len(all_lines)} lines in {log_path} matched the "
            f"expected sledgehammer log format; produced 0 entries. "
            f"Is this actually a mirabelle.log?",
            file=sys.stderr,
        )
    return entries


def count_by(items: Iterable[str]) -> collections.Counter[str]:
    return collections.Counter(items)


def render_summary(log_entries: list[LogEntry]) -> str:
    lines: list[str] = []

    lines.append("# output_mirabelle summary")
    lines.append("")

    if log_entries:
        outcome_counts = count_by(entry.outcome for entry in log_entries)
        backend_counts = count_by(
            entry.suggested_backend
            for entry in log_entries
            if entry.suggested_backend is not None
        )
        lines.append("## Mirabelle log")
        lines.append(f"- goals: {len(log_entries)}")
        lines.append(
            f"- outcomes: success preplay={outcome_counts.get('success preplay', 0)}, "
            f"failure preplay={outcome_counts.get('failure preplay', 0)}, "
            f"timeout={outcome_counts.get('timeout', 0)}, "
            f"prover error={outcome_counts.get('prover error', 0)}, "
            f"other error={outcome_counts.get('other error', 0)}"
        )
        if backend_counts:
            backend_text = ", ".join(
                f"{backend}={count}"
                for backend, count in backend_counts.most_common()
            )
            lines.append(f"- suggested SMT backends: {backend_text}")
        strategy_counts = count_by(
            entry.strategy
            for entry in log_entries
            if entry.strategy is not None
        )
        if strategy_counts:
            strategy_text = ", ".join(
                f"{s}={c}" for s, c in strategy_counts.most_common()
            )
            lines.append(f"- SMT strategies: {strategy_text}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def json_payload(log_entries: list[LogEntry]) -> list[dict]:
    return [
        {
            "session": entry.ref.session,
            "theory": entry.ref.theory,
            "base": entry.ref.base,
            "line": entry.line,
            "outcome": entry.outcome,
            "suggested_backend": entry.suggested_backend,
            "strategy": entry.strategy,
            "sledgehammer_time": entry.sledgehammer_time,
            "atp_time": entry.atp_time,
            "preplay_command": entry.preplay_command,
            "preplay_time": entry.preplay_time,
            "calls": [
                {
                    "solver": call.solver,
                    "strategy": call.strategy,
                    "preplay_command": call.preplay_command,
                    "preplay_time": call.preplay_time,
                    "outcome": call.outcome,
                }
                for call in entry.calls
            ],
        }
        for entry in log_entries
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transform mirabelle.log into .json file."
    )
    parser.add_argument(
        "mirabelle_log",
        help="path to mirabelle.log",
    )
    parser.add_argument(
        "json_output",
        help="path for machine-readable JSON output",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    log_path = Path(args.mirabelle_log)
    try:
        log_entries = parse_mirabelle_log(log_path)
    except (FileNotFoundError, IsADirectoryError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not log_entries:
        print(
            f"warning: no log entries were parsed from {log_path}; "
            f"output will be empty.",
            file=sys.stderr,
        )

    summary = render_summary(log_entries)
    sys.stdout.write(summary)

    output_path = Path(args.json_output)
    try:
        if output_path.parent and not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(json_payload(log_entries), indent=2, sort_keys=True),
            encoding="utf-8",
        )
    except OSError as exc:
        print(
            f"error: could not write JSON output to {output_path}: {exc}",
            file=sys.stderr,
        )
        return 1

    print(
        f"wrote {len(log_entries)} entries to {output_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
