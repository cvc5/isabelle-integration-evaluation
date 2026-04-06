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


ARTIFACT_RE = re.compile(
    r"^(?P<base>prob_(?P<line>\d{5})_(?P<offset>\d{6}))__(?P<serial>\d+)\.smt_(?P<kind>in|out)$"
)
LOG_RE = re.compile(
    r"^\d+\.sledgehammer\s+goal\.[^\s]+\s+\d+ms\s+"
    r"(?P<theory>[A-Za-z0-9_.']+)\s+(?P<line>\d+):(?P<offset>\d+)\s+"
    r"(?P<outcome>some|timeout|none)\b"
)
SMT_BACKEND_RE = re.compile(r"Try this: (?:by|apply) \(smt \((?P<backend>[^)]*)\)")
RESULT_CODE_RE = re.compile(r'\("RESULT_CODE",\s*(-?\d+)\)')
RESULT_MSG_RE = re.compile(r'\("RESULT_MSG",\s*"([^"]*)"\)', re.DOTALL)

SESSION_NAME = "Scratch_Output_Mirabelle_Mini"
THEORY_NAME = "Scratch_output_mirabelle_mini"

OUTPUT_KIND_LABELS = {
    "unsat_with_proof": "unsat with proof text",
    "unsat_no_proof": "unsat without proof text",
    "sat_no_proof": "sat, so no proof available",
    "sat_other": "sat output",
    "unknown_no_proof": "unknown, so no proof available",
    "unknown_status_not_unsat": "unknown: status is not unsat",
    "unknown_other": "unknown output",
    "solver_error_int_pow2_missing_nla": "solver error: int.pow2 needs nonlinear arithmetic",
    "solver_error_generic": "solver error",
    "timeout_core_dump": "timeout with cvc5 abort/core dump",
    "timeout_interrupted": "timeout interrupted",
    "empty_output": "empty output",
    "other_output": "other output",
}

REPLAY_KIND_LABELS = {
    "replay_success": "replay success",
    "reconstruction_failure": "Alethe reconstruction failure",
    "reconstruction_timeout": "Alethe reconstruction timeout",
    "checker_error": "checker error",
    "checker_timeout": "checker timeout",
    "missing_input": "missing paired .smt_in file",
}

FAILURE_OUTPUT_KINDS = {
    "unsat_no_proof",
    "solver_error_int_pow2_missing_nla",
    "solver_error_generic",
    "timeout_core_dump",
    "timeout_interrupted",
    "empty_output",
    "other_output",
}

FAILURE_REPLAY_KINDS = {
    "reconstruction_failure",
    "reconstruction_timeout",
    "checker_error",
    "checker_timeout",
    "missing_input",
}


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
class ReplayResult:
    kind: str
    result_code: int | None
    result_msg: str | None


@dataclasses.dataclass
class Artifact:
    ref: ProblemRef
    serial: int
    out_path: Path
    in_path: Path | None = None
    output_kind: str = ""
    headline: str = ""
    second_line: str | None = None
    replay: ReplayResult | None = None


def relpath(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def theory_from_dir(dirname: str) -> str:
    return re.sub(r"^\d+_", "", dirname)


def parse_artifact_name(path: Path) -> tuple[ProblemRef, int, str] | None:
    match = ARTIFACT_RE.match(path.name)
    if match is None:
        return None

    session = path.parent.parent.name
    theory = theory_from_dir(path.parent.name)
    ref = ProblemRef(session=session, theory=theory, base=match.group("base"))
    serial = int(match.group("serial"))
    kind = match.group("kind")
    return ref, serial, kind


def classify_output(text: str) -> tuple[str, str, str | None]:
    lines = text.splitlines()
    if not lines:
        return "empty_output", "", None

    first = lines[0].strip()
    second = lines[1].strip() if len(lines) > 1 else None

    if first == "unsat":
        return ("unsat_with_proof" if len(lines) > 1 else "unsat_no_proof", first, second)
    if first == "sat":
        if second == '(error "cannot get proof unless in unsat mode.")':
            return "sat_no_proof", first, second
        return "sat_other", first, second
    if first == "unknown":
        if second == '(error "cannot get proof unless in unsat mode.")':
            return "unknown_no_proof", first, second
        if second == '(error "status is not unsat.")':
            return "unknown_status_not_unsat", first, second
        return "unknown_other", first, second
    if "Term of kind int.pow2 requires the logic to include non-linear arithmetic" in first:
        return "solver_error_int_pow2_missing_nla", first, second
    if first == "cvc5 interrupted by timeout.":
        if "core dumped" in text or "Aborted" in text:
            return "timeout_core_dump", first, second
        return "timeout_interrupted", first, second
    if first.startswith("(error "):
        return "solver_error_generic", first, second
    return "other_output", first, second


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


def default_isabelle_binary(repo_root: Path) -> Path | None:
    candidate = repo_root / "bin" / "isabelle"
    return candidate if candidate.is_file() else None


def isabelle_escape(path: Path) -> str:
    return str(path).replace("\\", "\\\\").replace('"', '\\"')


def replay_theory_text(
    import_theory: str,
    in_path: Path,
    out_path: Path,
    timeout_seconds: int,
    result_file: Path,
) -> str:
    return textwrap.dedent(
        f"""\
        theory {THEORY_NAME}
          imports "{import_theory}"
        begin

        ML \<open>
        let
          val replay_timeout = Time.fromSeconds {timeout_seconds}
          val result_path = "{isabelle_escape(result_file)}"
          val base_ctxt =
            @{{context}}
            |> Config.put SMT_Config.check_external true
            |> SMT_Config.alethe_set_no_provided_assms true
          val problem_lines =
            Bytes.read (Path.explode "{isabelle_escape(in_path)}") |> Bytes.split_lines
          val proof_lines =
            Bytes.read (Path.explode "{isabelle_escape(out_path)}") |> Bytes.split_lines

          fun sanitize s =
            String.translate
              (fn c =>
                if c = #"\\t" orelse c = #"\\n" orelse c = #"\\r"
                then " "
                else str c) s

          fun emit code msg =
            File_Stream.open_output
              (fn stream =>
                File_Stream.outputs stream
                  [Int.toString code ^ "\\t" ^ sanitize msg ^ "\\n"])
              (Path.explode result_path)

          fun classify exn =
            (case exn of
              SMT_Parse_Problem.SMT_PROBLEM_PARSE msg =>
                if String.isPrefix "command not supported: " msg
                then (5, "Unsupported SMT-LIB command in problem: " ^ msg)
                else (5, "Error parsing SMT-LIB problem: " ^ msg)
            | SMTLIB.PARSE (line, err) =>
                (5, "Error parsing SMTLIB into SMTLIB Tree: " ^ err ^ " in line " ^ Int.toString line)
            | SMTLIB_Proof.SMTLIB_PARSE ("unknown SMT type", t) =>
                (2, "Either theory is not supported or parsing instructions for the type are not included in the parser " ^ SMTLIB.str_of t)
            | SMTLIB_Proof.SMTLIB_PARSE ("bad SMT term", t) =>
                (3, "Either theory is not supported or parsing instructions for the term are not included in the parser " ^ SMTLIB.str_of t)
            | SMTLIB_Proof.SMTLIB_PARSE (err, t) =>
                (4, "Unkown error parsing SMTLIB: " ^ err ^ SMTLIB.str_of t)
            | SMT_Failure.SMT (SMT_Failure.Replay (rule, ERROR msg)) =>
                (6, "Error replaying step " ^ rule ^ ": " ^ msg)
            | SMT_Failure.SMT (SMT_Failure.Replay (rule, Exn.Interrupt_Breakdown)) =>
                (7, "Error replaying step " ^ rule ^ ": interrupt while replaying step")
            | SMT_Failure.SMT (SMT_Failure.Replay (rule, exn')) =>
                (7, "Error replaying step " ^ rule ^ ": " ^ General.exnMessage exn')
            | SMT_Failure.SMT (SMT_Failure.Time_Out rule) =>
                (7, "Error replaying step " ^ rule ^ ": timeout while reconstructing rule")
            | Timeout.TIMEOUT _ =>
                (7, "Timeout")
            | TYPE (msg, _, _) =>
                (1, "Type Error " ^ msg)
            | Size =>
                (1, "Size")
            | ERROR msg =>
                (1, "Error " ^ msg)
            | exn' =>
                (1, "Unhandled exception " ^ General.exnMessage exn'))

          val (code, msg) =
            (Timeout.apply replay_timeout
              (fn () =>
                (SMT_Check_External.replay_only "cvc5_proof" base_ctxt problem_lines proof_lines NONE;
                 (0, ""))) ()
             handle exn => classify exn)

          val _ = emit code msg
        in
          ()
        end
        \<close>

        end
        """
    )


def classify_replay_result(returncode: int, output: str) -> ReplayResult:
    code_match = RESULT_CODE_RE.search(output)
    msg_match = RESULT_MSG_RE.search(output)

    code = int(code_match.group(1)) if code_match else None
    msg = msg_match.group(1).replace("\n", " ").strip() if msg_match else None

    return classify_replay_code_msg(code, msg, returncode)


def classify_replay_code_msg(
    code: int | None,
    msg: str | None,
    returncode: int | None = None,
) -> ReplayResult:
    if code is None and returncode == 0:
        code = 0

    if code == 0:
        return ReplayResult("replay_success", 0, msg)
    if msg and msg.startswith("Error replaying step"):
        if "timeout" in msg.lower():
            return ReplayResult("reconstruction_timeout", code, msg)
        return ReplayResult("reconstruction_failure", code, msg)
    if msg == "Timeout":
        return ReplayResult("checker_timeout", code, msg)
    if msg is not None:
        return ReplayResult("checker_error", code, msg)
    return ReplayResult("checker_error", code, f"isabelle build returned {returncode}")


def replay_one_artifact(
    repo_root: Path,
    isabelle_binary: Path,
    import_theory: str,
    timeout_seconds: int,
    artifact: Artifact,
) -> ReplayResult:
    if artifact.in_path is None:
        return ReplayResult("missing_input", None, "missing paired .smt_in file")

    with tempfile.TemporaryDirectory(prefix="mirabelle_mini_") as tmp:
        session_root = Path(tmp)
        root_file = session_root / "ROOT"
        theory_file = session_root / f"{THEORY_NAME}.thy"
        result_file = session_root / "result.tsv"

        root_file.write_text(
            textwrap.dedent(
                f"""\
                session {SESSION_NAME} = HOL +
                  theories {THEORY_NAME}
                """
            ),
            encoding="utf-8",
        )
        theory_file.write_text(
            replay_theory_text(
                import_theory,
                artifact.in_path,
                artifact.out_path,
                timeout_seconds,
                result_file,
            ),
            encoding="utf-8",
        )

        command = [
            str(isabelle_binary),
            "build",
            "-v",
            "-d",
            str(repo_root / "src" / "HOL"),
            "-d",
            str(session_root),
            SESSION_NAME,
        ]
        build_timeout = max(120, timeout_seconds + 60)

        try:
            completed = subprocess.run(
                command,
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=build_timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return ReplayResult("checker_timeout", None, f"batch timeout after {build_timeout}s")

        output = completed.stdout + completed.stderr
        if result_file.is_file():
            line = result_file.read_text(errors="replace").splitlines()
            if line:
                parts = line[0].split("\t", 1)
                try:
                    code = int(parts[0])
                except ValueError:
                    code = None
                msg = parts[1] if len(parts) > 1 and parts[1] != "" else None
                return classify_replay_code_msg(code, msg, completed.returncode)

    output = completed.stdout + completed.stderr
    return classify_replay_result(completed.returncode, output)


def select_replay_artifacts(
    artifacts: list[Artifact],
    log_entries: list[LogEntry],
    selection: str,
    limit: int | None,
) -> list[Artifact]:
    candidates = [
        artifact
        for artifact in artifacts
        if artifact.output_kind == "unsat_with_proof"
    ]

    if selection == "one-per-goal":
        some_refs = {entry.ref for entry in log_entries if entry.outcome == "some"}
        if some_refs:
            candidates = [artifact for artifact in candidates if artifact.ref in some_refs]

        chosen: list[Artifact] = []
        seen: set[ProblemRef] = set()
        for artifact in sorted(
            candidates,
            key=lambda a: (a.ref.session, a.ref.theory, a.ref.base, a.serial),
        ):
            if artifact.ref in seen:
                continue
            seen.add(artifact.ref)
            chosen.append(artifact)
        candidates = chosen
    elif selection != "all":
        raise ValueError(f"unknown replay selection: {selection}")

    if limit is not None:
        candidates = candidates[:limit]
    return candidates


def run_replay(
    repo_root: Path,
    artifacts: list[Artifact],
    log_entries: list[LogEntry],
    isabelle_binary: Path,
    import_theory: str,
    timeout_seconds: int,
    selection: str,
    limit: int | None,
) -> None:
    selected = select_replay_artifacts(artifacts, log_entries, selection, limit)
    for index, artifact in enumerate(selected, start=1):
        print(
            f"[replay {index}/{len(selected)}] {artifact.ref.session}/{artifact.ref.theory}/{artifact.ref.base}__{artifact.serial}",
            file=sys.stderr,
        )
        artifact.replay = replay_one_artifact(
            repo_root=repo_root,
            isabelle_binary=isabelle_binary,
            import_theory=import_theory,
            timeout_seconds=timeout_seconds,
            artifact=artifact,
        )


def count_by(items) -> collections.Counter:
    return collections.Counter(items)


def is_failure(artifact: Artifact) -> bool:
    if artifact.output_kind in FAILURE_OUTPUT_KINDS:
        return True
    if artifact.replay is not None and artifact.replay.kind in FAILURE_REPLAY_KINDS:
        return True
    return False


def matching_log_entry(log_entries: list[LogEntry], ref: ProblemRef) -> LogEntry | None:
    for entry in log_entries:
        if entry.ref == ref:
            return entry
    return None


def shorten(text: str | None, limit: int = 140) -> str | None:
    if text is None or len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def render_summary(
    repo_root: Path,
    artifacts: list[Artifact],
    log_entries: list[LogEntry],
    examples: int,
    failures_only: bool,
) -> str:
    visible = [artifact for artifact in artifacts if is_failure(artifact)] if failures_only else artifacts
    lines: list[str] = ["# output_mirabelle mini summary", ""]

    if log_entries:
        outcome_counts = count_by(entry.outcome for entry in log_entries)
        backend_counts = count_by(
            entry.suggested_backend for entry in log_entries if entry.suggested_backend
        )
        lines.append("## Mirabelle")
        lines.append(f"- goals: {len(log_entries)}")
        lines.append(
            f"- outcomes: some={outcome_counts.get('some', 0)}, timeout={outcome_counts.get('timeout', 0)}, none={outcome_counts.get('none', 0)}"
        )
        if backend_counts:
            backends = ", ".join(f"{name}={count}" for name, count in backend_counts.most_common())
            lines.append(f"- suggested backends: {backends}")
        lines.append("")

    lines.append("## Artifacts")
    lines.append(f"- shown artifacts: {len(visible)}")
    lines.append(f"- total saved .smt_out files: {len(artifacts)}")
    for kind, count in count_by(artifact.output_kind for artifact in visible).most_common():
        lines.append(f"- {OUTPUT_KIND_LABELS.get(kind, kind)}: {count}")
    lines.append("")

    replayed = [artifact for artifact in visible if artifact.replay is not None]
    if replayed:
        lines.append("## Replay")
        lines.append(f"- replayed artifacts: {len(replayed)}")
        for kind, count in count_by(artifact.replay.kind for artifact in replayed).most_common():
            lines.append(f"- {REPLAY_KIND_LABELS.get(kind, kind)}: {count}")
        lines.append("")

    lines.append("## Examples")
    if not visible:
        lines.append("- none")
    else:
        for artifact in visible[:examples]:
            parts = [relpath(artifact.out_path, repo_root)]
            if artifact.in_path is not None:
                parts.append(f"in={relpath(artifact.in_path, repo_root)}")
            parts.append(f"output_kind={artifact.output_kind}")
            if artifact.replay is not None:
                parts.append(f"replay={artifact.replay.kind}")
                if artifact.replay.result_msg:
                    parts.append(f"msg={shorten(artifact.replay.result_msg)}")
            elif artifact.second_line:
                parts.append(f"detail={shorten(artifact.second_line)}")

            log_entry = matching_log_entry(log_entries, artifact.ref)
            if log_entry is not None:
                parts.append(f"goal_outcome={log_entry.outcome}")
            lines.append(f"- {' | '.join(parts)}")
    lines.append("")

    return "\n".join(lines)


def json_payload(
    repo_root: Path,
    artifacts: list[Artifact],
    log_entries: list[LogEntry],
    failures_only: bool,
) -> dict:
    visible = [artifact for artifact in artifacts if is_failure(artifact)] if failures_only else artifacts
    log_map = {entry.ref: entry for entry in log_entries}

    return {
        "scope": {
            "failures_only": failures_only,
            "note": "Mini analyzer output. Replay, if present, was run one artifact per Isabelle build.",
        },
        "counts": {
            "artifacts": len(visible),
            "output_kind": dict(count_by(artifact.output_kind for artifact in visible)),
            "replay_kind": dict(
                count_by(artifact.replay.kind for artifact in visible if artifact.replay is not None)
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
            for artifact in visible
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Small, readable analyzer for output_mirabelle."
    )
    parser.add_argument("output_dir", nargs="?", default="output_mirabelle")
    parser.add_argument("--mirabelle-log", default=None)
    parser.add_argument("--json", default=None, help="write machine-readable JSON")
    parser.add_argument(
        "--failures-only",
        action="store_true",
        help="show only explicit solver/replay failures",
    )
    parser.add_argument("--examples", type=int, default=5)
    parser.add_argument(
        "--replay",
        action="store_true",
        help="replay saved unsat proofs in Isabelle (simple and slower than the full analyzer)",
    )
    parser.add_argument("--isabelle", default=None)
    parser.add_argument("--import-theory", default="HOL.SMT_CVC")
    parser.add_argument("--replay-timeout", type=int, default=90)
    parser.add_argument(
        "--selection",
        choices=["all", "one-per-goal"],
        default="one-per-goal",
        help="which saved proof artifacts to replay",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="limit the number of replayed artifacts",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    output_root = (repo_root / args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir).resolve()
    log_path = (
        Path(args.mirabelle_log).resolve()
        if args.mirabelle_log
        else (output_root / "mirabelle.log").resolve()
    )

    if not output_root.is_dir():
        print(f"output directory not found: {output_root}", file=sys.stderr)
        return 2

    artifacts = collect_artifacts(output_root)
    log_entries = parse_mirabelle_log(log_path)

    if args.replay:
        isabelle_binary = Path(args.isabelle).resolve() if args.isabelle else default_isabelle_binary(repo_root)
        if isabelle_binary is None or not isabelle_binary.is_file():
            print("no Isabelle binary found; pass --isabelle /path/to/bin/isabelle", file=sys.stderr)
            return 2
        run_replay(
            repo_root=repo_root,
            artifacts=artifacts,
            log_entries=log_entries,
            isabelle_binary=isabelle_binary,
            import_theory=args.import_theory,
            timeout_seconds=args.replay_timeout,
            selection=args.selection,
            limit=args.limit,
        )

    summary = render_summary(
        repo_root=repo_root,
        artifacts=artifacts,
        log_entries=log_entries,
        examples=max(args.examples, 0),
        failures_only=args.failures_only,
    )
    sys.stdout.write(summary)

    if args.json:
        json_path = Path(args.json)
        if not json_path.is_absolute():
            json_path = repo_root / json_path
        json_path.write_text(
            json.dumps(
                json_payload(
                    repo_root=repo_root,
                    artifacts=artifacts,
                    log_entries=log_entries,
                    failures_only=args.failures_only,
                ),
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
