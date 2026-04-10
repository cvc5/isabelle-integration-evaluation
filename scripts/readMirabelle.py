#!/usr/bin/env python3
import dataclasses
import collections
import json
from pathlib import Path
import argparse
import re

LOG_RE = re.compile(
    r"^\d+\.sledgehammer\s+goal\.[^\s]+\s+\d+ms\s+"
    r"(?P<theory>[A-Za-z0-9_.']+)\s+(?P<line>\d+):(?P<offset>\d+)\s+"
    r"(?P<outcome>some|timeout|none)\b"
)
SMT_BACKEND_RE = re.compile(r"Try this: (?:by|apply) \(smt \((?P<backend>[^)]*)\)")

def count_by(items) -> collections.Counter:
    return collections.Counter(items)

@dataclasses.dataclass(frozen=True)
class ProblemRef:
    session: str
    theory: str
    base: str

@dataclasses.dataclass
class LogEntry:
    ref: ProblemRef
    theory_long_name: str
    outcome: str
    suggested_backend: str | None
    line_text: str

@dataclasses.dataclass
class Artifact:
    ref: ProblemRef
    serial: int
    out_path: Path
    in_path: Path | None = None
    output_kind: str = ""
    headline: str = ""
    second_line: str | None = None


def json_payload(
    repo_root: Path,
    artifacts: list[Artifact],
    log_entries: list[LogEntry],
) -> dict:
    log_map = {entry.ref: entry for entry in log_entries}

    return {
        "scope": {
            "note": "Mini analyzer output. Replay, if present, was run one artifact per Isabelle build.",
        },
        "counts": {
            "artifacts": len(artifacts),
            "output_kind": dict(count_by(artifact.output_kind for artifact in artifacts)),
            "replay_kind": dict(
                count_by(artifact.replay.kind for artifact in artifacts if artifact.replay is not None)
            ),
        },
        "artifacts": [
            {
                "session": artifact.ref.session,
                "theory": artifact.ref.theory,
                "base": artifact.ref.base,
                "serial": artifact.serial,
                "out_path": relpath(artifact.out_path, repo_root),
                "in_path": relpath(artifact.in_path, repo_root) if artifact.in_path else None,
                "output_kind": artifact.output_kind,
                "headline": artifact.headline,
                "second_line": artifact.second_line,
                "replay": None
                if artifact.replay is None
                else {
                    "kind": artifact.replay.kind,
                    "result_code": artifact.replay.result_code,
                    "result_msg": artifact.replay.result_msg,
                },
                "mirabelle": None
                if artifact.ref not in log_map
                else {
                    "outcome": log_map[artifact.ref].outcome,
                    "suggested_backend": log_map[artifact.ref].suggested_backend,
                    "theory_long_name": log_map[artifact.ref].theory_long_name,
                    "line_text": log_map[artifact.ref].line_text,
                },
            }
            for artifact in artifacts
        ],
    }

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
            backend = backend_match.group("backend").split(",", 1)[0].strip()

        entries.append(
            LogEntry(
                ref=ref,
                theory_long_name=theory_long_name,
                outcome=match.group("outcome"),
                suggested_backend=backend,
                line_text=line,
            )
        )
    return entries

def collect_artifacts(output_root: Path) -> list[Artifact]:
    inputs: dict[tuple[ProblemRef, int], Path] = {}
    outputs: dict[tuple[ProblemRef, int], Path] = {}

    for path in sorted(output_root.rglob("*.smt_in")):
        parsed = parse_artifact_name(path)
        if parsed is None:
            continue
        ref, serial, kind = parsed
        if kind == "in":
            inputs[(ref, serial)] = path

    for path in sorted(output_root.rglob("*.smt_out")):
        parsed = parse_artifact_name(path)
        if parsed is None:
            continue
        ref, serial, kind = parsed
        if kind == "out":
            outputs[(ref, serial)] = path

    artifacts: list[Artifact] = []
    for (ref, serial), out_path in sorted(
        outputs.items(),
        key=lambda item: (item[0][0].session, item[0][0].theory, item[0][0].base, item[0][1]),
    ):
        text = out_path.read_text(errors="replace")
        output_kind, headline, second_line = classify_output(text)
        artifacts.append(
            Artifact(
                ref=ref,
                serial=serial,
                out_path=out_path,
                in_path=inputs.get((ref, serial)),
                output_kind=output_kind,
                headline=headline,
                second_line=second_line,
            )
        )
    return artifacts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read a mirabelle log file and generate .json file from the information"
    )
    parser.add_argument("--mirabelle-log", required=True, help="path to the mirabelle.log file")
    parser.add_argument("--mirabelle-dir", required=True, help="path to the output directory the mirabelle run created, e.g., 0.sledgehammer" )
    parser.add_argument("--json", required=True, help="write machine-readable JSON to this filepath")
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    mirabelle_log_path = (
        Path(args.mirabelle_log).resolve()
    )
    mirabelle_output_dir = (
        Path(args.mirabelle_dir).resolve()
    )
 
    artifacts = collect_artifacts(mirabelle_output_dir)
    log_entries = parse_mirabelle_log(mirabelle_log_path)


    if args.json:
        json_path = Path(args.json)
        json_path.write_text(
            json.dumps(
                json_payload(
                    repo_root=mirabelle_output_dir,
                    artifacts=artifacts,
                    log_entries=log_entries,
                ),
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    return 0



if __name__ == "__main__":
    raise SystemExit(main())
