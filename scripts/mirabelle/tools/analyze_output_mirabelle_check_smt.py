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

SESSION_NAME = "Scratch_Output_Mirabelle_Check"
THEORY_NAME = "Scratch_output_mirabelle_check"


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
    "proof_parse_or_context_failure": "problem/proof parse or context failure",
    "checker_error": "checker error",
    "checker_timeout": "checker timeout",
    "missing_input": "missing paired .smt_in file",
    "replay_skipped": "replay skipped",
}


@dataclasses.dataclass(frozen=True)
class ProblemRef:
    session: str
    theory: str
    base: str


@dataclasses.dataclass
class Artifact:
    out_path: Path
    ref: ProblemRef
    out_serial: int
    in_path: Path | None = None
    in_serial: int | None = None
    output_kind: str = ""
    headline: str = ""
    second_line: str | None = None
    replay: "ReplayResult | None" = None


@dataclasses.dataclass
class LogEntry:
    ref: ProblemRef
    outcome: str
    theory_long_name: str
    line_text: str
    suggested_backend: str | None


@dataclasses.dataclass
class ReplayResult:
    kind: str
    result_code: int | None
    result_msg: str | None
    build_output: str


def relpath(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def theory_from_dir(dirname: str) -> str:
    return re.sub(r"^\d+_", "", dirname)


def parse_artifact_path(path: Path) -> tuple[ProblemRef, int, str] | None:
    match = ARTIFACT_RE.match(path.name)
    if match is None:
        return None
    session = path.parent.parent.name
    theory = theory_from_dir(path.parent.name)
    ref = ProblemRef(session=session, theory=theory, base=match.group("base"))
    return ref, int(match.group("serial")), match.group("kind")


def classify_output(text: str) -> tuple[str, str, str | None]:
    lines = text.splitlines()
    if not lines:
        return "empty_output", "", None

    first = lines[0].strip()
    second = lines[1].strip() if len(lines) > 1 else None

    if first == "unsat":
        if len(lines) > 1:
            return "unsat_with_proof", first, second
        return "unsat_no_proof", first, second
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
    inputs: dict[ProblemRef, list[tuple[int, Path]]] = collections.defaultdict(list)
    outputs: dict[ProblemRef, list[tuple[int, Path]]] = collections.defaultdict(list)

    for path in sorted(output_root.rglob("*.smt_in")):
        parsed = parse_artifact_path(path)
        if parsed is None:
            continue
        ref, serial, kind = parsed
        if kind == "in":
            inputs[ref].append((serial, path))

    for path in sorted(output_root.rglob("*.smt_out")):
        parsed = parse_artifact_path(path)
        if parsed is None:
            continue
        ref, serial, kind = parsed
        if kind != "out":
            continue
        outputs[ref].append((serial, path))

    artifacts: list[Artifact] = []
    for ref, grouped_outputs in sorted(outputs.items(), key=lambda item: (item[0].session, item[0].theory, item[0].base)):
        grouped_inputs = sorted(inputs.get(ref, []))
        unused_inputs = set(range(len(grouped_inputs)))

        for out_serial, out_path in sorted(grouped_outputs):
            chosen_index: int | None = None
            candidate_indices = [i for i in unused_inputs if grouped_inputs[i][0] <= out_serial]
            if candidate_indices:
                chosen_index = max(candidate_indices, key=lambda i: grouped_inputs[i][0])
            elif unused_inputs:
                chosen_index = min(unused_inputs, key=lambda i: abs(grouped_inputs[i][0] - out_serial))
            elif grouped_inputs:
                chosen_index = min(range(len(grouped_inputs)), key=lambda i: abs(grouped_inputs[i][0] - out_serial))

            if chosen_index is not None and chosen_index in unused_inputs:
                unused_inputs.remove(chosen_index)

            artifact = Artifact(out_path=out_path, ref=ref, out_serial=out_serial)
            if chosen_index is not None:
                artifact.in_serial, artifact.in_path = grouped_inputs[chosen_index]

            text = out_path.read_text(errors="replace")
            artifact.output_kind, artifact.headline, artifact.second_line = classify_output(text)
            artifacts.append(artifact)

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


def prepare_replay_session(repo_root: Path, session_root: Path, import_theory: str, session_name: str) -> tuple[Path, Path]:
    root_file = session_root / "ROOT"
    theory_file = session_root / f"{THEORY_NAME}.thy"
    root_file.write_text(
        textwrap.dedent(
            f"""\
            session {session_name} = HOL +
              theories {THEORY_NAME}
            """
        ),
        encoding="utf-8",
    )
    theory_file.write_text(
        textwrap.dedent(
            f"""\
            theory {THEORY_NAME}
              imports "{import_theory}"
            begin

            lemma replay_placeholder: "True"
              by simp

            end
            """
        ),
        encoding="utf-8",
    )
    return root_file, theory_file


def theory_text(import_theory: str, in_path: Path, out_path: Path) -> str:
    return textwrap.dedent(
        f"""\
        theory {THEORY_NAME}
          imports "{import_theory}"
        begin

        check_smt ("cvc5_proof")
          "{isabelle_string(in_path)}"
          "{isabelle_string(out_path)}"

        end
        """
    )


def classify_replay_code_msg(code: int | None, msg: str | None, returncode: int | None = None) -> tuple[int | None, str | None, str]:
    if code is None and returncode == 0:
        code = 0
    if code == 0:
        return code, msg, "replay_success"
    if msg and msg.startswith("Error replaying step"):
        if "timeout" in msg.lower():
            return code, msg, "reconstruction_timeout"
        return code, msg, "reconstruction_failure"
    if msg == "Timeout":
        return code, msg, "checker_timeout"
    if msg in {"unknown SMT type", "bad SMT term", "Unsupported SMT-LIB command", "Error parsing SMT-LIB problem", "Error parsing SMTLIB into SMTLIB Tree", "Unkown error parsing SMTLIB"}:
        return code, msg, "proof_parse_or_context_failure"
    if msg in {"Error", "Type Error", "Size", "Unkown SMT error"}:
        return code, msg, "checker_error"
    return code, msg, "checker_error"


def classify_replay_result(returncode: int | None, stdout: str) -> tuple[int | None, str | None, str]:
    code_match = RESULT_CODE_RE.search(stdout)
    msg_match = RESULT_MSG_RE.search(stdout)
    code = int(code_match.group(1)) if code_match else None
    msg = msg_match.group(1).replace("\n", " ").strip() if msg_match else None
    return classify_replay_code_msg(code, msg, returncode)


def batch_theory_text(
    import_theory: str,
    batch_artifacts: list[Artifact],
    result_file: Path,
    replay_timeout: int,
) -> str:
    entries_text = ",\n        ".join(
        f'({index}, "{isabelle_string(artifact.in_path)}", "{isabelle_string(artifact.out_path)}", "{isabelle_string(result_file.with_name(f"check_{index}.txt"))}")'
        for index, artifact in enumerate(batch_artifacts)
        if artifact.in_path is not None
    )
    return textwrap.dedent(
        f"""\
        theory {THEORY_NAME}
          imports "{import_theory}"
        begin

        ML \<open>
        let
          val result_path = "{isabelle_string(result_file)}"
          val replay_timeout = Time.fromSeconds {replay_timeout}

          fun sanitize s =
            String.translate
              (fn c =>
                if c = #"\\t" orelse c = #"\\n" orelse c = #"\\r"
                then " "
                else str c) s

          fun emit idx code msg =
            File_Stream.open_append
              (fn stream =>
                File_Stream.outputs stream
                  [Int.toString idx ^ "\\t" ^ Int.toString code ^ "\\t" ^ sanitize msg ^ "\\n"])
              (Path.explode result_path)

          fun last_path_component path =
            (case rev (String.tokens (fn c => c = #"/") path) of
              [] => path
            | name :: _ => name)

          fun success_message check_text =
            (case rev (String.tokens
                (fn c => c = #"," orelse c = #" " orelse c = #"\\n" orelse c = #"\\r" orelse c = #"\\t")
                check_text) of
              time_ns :: _ =>
                if time_ns <> "" andalso List.all Char.isDigit (String.explode time_ns)
                then SOME ("check_smt success parsing_time_ns=" ^ time_ns)
                else NONE
            | [] => NONE)

          fun replay_one (idx, problem_path, proof_path, check_path) =
            let
              val lthy = Named_Target.theory_init @{{theory}}
              val check_file = Path.explode check_path
              val base_name = last_path_component problem_path
              val (code, msg) =
                (Timeout.apply replay_timeout
                  (fn () =>
                    let
                      val _ = Bytes.write check_file Bytes.empty
                      val _ = SMT_Check_External.check_smt "cvc5_proof" problem_path proof_path (SOME check_path) lthy
                      val check_text = if File.exists check_file then File.read check_file else ""
                    in
                      (case success_message check_text of
                        SOME msg => (0, msg)
                      | NONE =>
                          (1,
                           "check_smt failed without parsing time for " ^ base_name ^
                           "; raw_output=" ^ sanitize check_text))
                    end) ()
                 handle exn => (2, "exception while running check_smt on " ^ base_name ^ ": " ^ General.exnMessage exn))
            in
              emit idx code msg
            end

          val entries = [
            {entries_text}
          ]
        in
          List.app replay_one entries
        end
        \<close>

        end
        """
    )


def select_replay_artifacts(
    artifacts: list[Artifact],
    log_entries: list[LogEntry],
    replay_selection: str,
) -> list[Artifact]:
    unsat_artifacts = [artifact for artifact in artifacts if artifact.output_kind == "unsat_with_proof"]
    if replay_selection == "all":
        return unsat_artifacts

    selected: list[Artifact] = []
    if replay_selection == "one-per-goal":
        some_refs = {entry.ref for entry in log_entries if entry.outcome == "some"}
        relevant = [artifact for artifact in unsat_artifacts if artifact.ref in some_refs] or unsat_artifacts
        seen: set[ProblemRef] = set()
        for artifact in sorted(relevant, key=lambda artifact: (artifact.ref.session, artifact.ref.theory, artifact.ref.base, artifact.out_serial)):
            if artifact.ref in seen:
                continue
            seen.add(artifact.ref)
            selected.append(artifact)
        return selected

    raise ValueError(f"unknown replay selection: {replay_selection}")


def replay_unsat_artifacts(
    repo_root: Path,
    artifacts: list[Artifact],
    log_entries: list[LogEntry],
    isabelle_binary: Path,
    import_theory: str,
    replay_timeout: int,
    replay_selection: str,
    replay_batch_size: int,
) -> None:
    selected_artifacts = select_replay_artifacts(artifacts, log_entries, replay_selection)
    if not selected_artifacts:
        return

    with tempfile.TemporaryDirectory(prefix="mirabelle_replay_") as tmp:
        session_root = Path(tmp)
        _, theory_file = prepare_replay_session(repo_root, session_root, import_theory, SESSION_NAME)
        hol_root = repo_root / "src" / "HOL"
        for artifact in selected_artifacts:
            if artifact.in_path is None:
                artifact.replay = ReplayResult(
                    kind="missing_input",
                    result_code=None,
                    result_msg="missing paired .smt_in file",
                    build_output="",
                )

        pending = [artifact for artifact in selected_artifacts if artifact.replay is None]
        batch_size = max(replay_batch_size, 1)
        total_batches = (len(pending) + batch_size - 1) // batch_size

        for batch_index in range(total_batches):
            batch = pending[batch_index * batch_size : (batch_index + 1) * batch_size]
            result_file = session_root / "batch_results.tsv"
            result_file.write_text("", encoding="utf-8")

            print(
                f"[replay batch {batch_index + 1}/{total_batches}] selected_proofs={len(batch)} selection={replay_selection}",
                file=sys.stderr,
            )
            theory_file.write_text(
                batch_theory_text(import_theory, batch, result_file, replay_timeout),
                encoding="utf-8",
            )

            command = [
                str(isabelle_binary),
                "build",
                "-v",
                "-d",
                str(hol_root),
                "-d",
                str(session_root),
                SESSION_NAME,
            ]
            build_timeout = max(120, replay_timeout * max(len(batch), 1) + 120)
            try:
                completed = subprocess.run(
                    command,
                    cwd=repo_root,
                    capture_output=True,
                    text=True,
                    timeout=build_timeout,
                    check=False,
                )
                build_output = completed.stdout + completed.stderr
            except subprocess.TimeoutExpired as exc:
                build_output = (exc.stdout or "") + (exc.stderr or "")
                for artifact in batch:
                    artifact.replay = ReplayResult(
                        kind="checker_timeout",
                        result_code=None,
                        result_msg=f"batch timeout after {build_timeout}s",
                        build_output=build_output,
                    )
                continue

            results_by_index: dict[int, ReplayResult] = {}
            for line in result_file.read_text(errors="replace").splitlines():
                parts = line.split("\t", 2)
                if len(parts) != 3:
                    continue
                try:
                    result_index = int(parts[0])
                    code = int(parts[1])
                except ValueError:
                    continue
                msg = parts[2] or None
                result_code, result_msg, kind = classify_replay_code_msg(code, msg, completed.returncode)
                results_by_index[result_index] = ReplayResult(
                    kind=kind,
                    result_code=result_code,
                    result_msg=result_msg,
                    build_output=build_output,
                )

            for index, artifact in enumerate(batch):
                artifact.replay = results_by_index.get(
                    index,
                    ReplayResult(
                        kind="checker_error",
                        result_code=None,
                        result_msg=(
                            "missing batch replay result"
                            if completed.returncode == 0
                            else f"missing batch replay result (build return code {completed.returncode})"
                        ),
                        build_output=build_output,
                    ),
                )


def count_by(items: Iterable[str]) -> collections.Counter[str]:
    return collections.Counter(items)


def shorten(text: str, limit: int = 180) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def format_artifact_example(artifact: Artifact, root: Path, *, include_detail: bool = True) -> str:
    parts = [relpath(artifact.out_path, root)]
    if artifact.in_path is not None:
        parts.append(f"in={relpath(artifact.in_path, root)}")
    if include_detail and artifact.second_line:
        parts.append(f"detail={shorten(artifact.second_line)}")
    return " | ".join(parts)


def format_replay_example(artifact: Artifact, root: Path) -> str:
    replay = artifact.replay
    assert replay is not None
    parts = [relpath(artifact.out_path, root)]
    if artifact.in_path is not None:
        parts.append(f"in={relpath(artifact.in_path, root)}")
    if replay.result_code is not None:
        parts.append(f"result_code={replay.result_code}")
    if replay.result_msg:
        parts.append(f"result_msg={replay.result_msg}")
    return " | ".join(parts)


def render_summary(
    repo_root: Path,
    output_root: Path,
    log_entries: list[LogEntry],
    artifacts: list[Artifact],
    examples_per_kind: int,
    replay_enabled: bool,
) -> str:
    lines: list[str] = []
    saved_proofs = [artifact for artifact in artifacts if artifact.output_kind == "unsat_with_proof"]
    proof_counts_by_ref = collections.Counter(artifact.ref for artifact in saved_proofs)
    replayed_selected = [artifact for artifact in saved_proofs if artifact.replay is not None]

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

    lines.append("## Alethe reconstruction diagnosis")
    lines.append(f"- cvc5 outputs with proof text: {len(saved_proofs)}")
    if log_entries:
        some_entries = [entry for entry in log_entries if entry.outcome == "some"]
        some_with_saved_proof = sum(1 for entry in some_entries if proof_counts_by_ref.get(entry.ref, 0) > 0)
        lines.append(
            f"- successful Mirabelle goals with at least one saved unsat proof artifact: {some_with_saved_proof} / {len(some_entries)}"
        )
        if proof_counts_by_ref:
            lines.append(
                f"- max saved unsat proof invocations for one goal: {max(proof_counts_by_ref.values())}"
            )
    if replay_enabled:
        replay_counts = count_by(
            artifact.replay.kind
            for artifact in replayed_selected
            if artifact.replay is not None
        )
        reconstruction_problem_kinds = {
            "reconstruction_failure",
            "reconstruction_timeout",
            "proof_parse_or_context_failure",
            "checker_error",
            "checker_timeout",
            "missing_input",
        }
        reconstruction_problem_count = sum(
            replay_counts.get(kind, 0) for kind in reconstruction_problem_kinds
        )
        lines.append(
            f"- selected saved unsat proofs for replay: {len(replayed_selected)} / {len(saved_proofs)}"
        )
        lines.append(
            f"- Isabelle replay success: {replay_counts.get('replay_success', 0)} / {len(replayed_selected)}"
        )
        lines.append(
            f"- reconstruction problems after proof generation: {reconstruction_problem_count} / {len(replayed_selected)}"
        )
        if replayed_selected and reconstruction_problem_count == 0:
            lines.append(
                "- conclusion: no selected saved case where cvc5 emitted proof text and Isabelle failed to reconstruct it"
            )
    else:
        lines.append("- replay not run")
    lines.append("")

    if saved_proofs:
        lines.append("## Example proof-producing files")
        for artifact in saved_proofs[:examples_per_kind]:
            if replay_enabled and artifact.replay is not None:
                lines.append(f"- {format_replay_example(artifact, repo_root)}")
            else:
                lines.append(f"- {format_artifact_example(artifact, repo_root, include_detail=False)}")
        lines.append("")

    output_kind_counts = count_by(artifact.output_kind for artifact in artifacts)
    lines.append("## Saved `.smt_out` files")
    lines.append(f"- files: {len(artifacts)}")
    for kind, count in output_kind_counts.most_common():
        lines.append(f"- {OUTPUT_KIND_LABELS.get(kind, kind)}: {count}")
    lines.append("")

    lines.append("## Solver-side and non-reconstruction kinds with example files")
    for kind, count in output_kind_counts.most_common():
        if kind == "unsat_with_proof":
            continue
        lines.append(f"### {OUTPUT_KIND_LABELS.get(kind, kind)} ({count})")
        examples = [artifact for artifact in artifacts if artifact.output_kind == kind][:examples_per_kind]
        if not examples:
            lines.append("- none")
            continue
        for artifact in examples:
            lines.append(f"- {format_artifact_example(artifact, repo_root)}")
    lines.append("")

    if log_entries:
        none_entries = [entry for entry in log_entries if entry.outcome == "none"]
        if none_entries:
            lines.append("## Mirabelle `none` entries")
            lines.append(f"- count: {len(none_entries)}")
            for entry in none_entries[:examples_per_kind]:
                lines.append(f"- {entry.line_text}")
            lines.append("")

    if replay_enabled:
        replay_counts = count_by(
            artifact.replay.kind
            for artifact in replayed_selected
            if artifact.replay is not None
        )
        lines.append("## Isabelle replay of selected saved unsat proofs")
        lines.append(f"- selected proofs: {len(replayed_selected)}")
        for kind, count in replay_counts.most_common():
            lines.append(f"- {REPLAY_KIND_LABELS.get(kind, kind)}: {count}")
        lines.append("")

        lines.append("## Replay failures with example files")
        failure_kinds = [
            kind
            for kind in replay_counts
            if kind not in {"replay_success", "replay_skipped"}
        ]
        if not failure_kinds:
            lines.append("- none")
        else:
            for kind in sorted(failure_kinds):
                lines.append(f"### {REPLAY_KIND_LABELS.get(kind, kind)} ({replay_counts[kind]})")
                examples = [
                    artifact
                    for artifact in replayed_selected
                    if artifact.replay is not None and artifact.replay.kind == kind
                ][:examples_per_kind]
                for artifact in examples:
                    lines.append(f"- {format_replay_example(artifact, repo_root)}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def json_payload(repo_root: Path, log_entries: list[LogEntry], artifacts: list[Artifact]) -> dict:
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
        "artifacts": [
            {
                "out_path": relpath(artifact.out_path, repo_root),
                "in_path": relpath(artifact.in_path, repo_root) if artifact.in_path else None,
                "session": artifact.ref.session,
                "theory": artifact.ref.theory,
                "base": artifact.ref.base,
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
            }
            for artifact in artifacts
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize output_mirabelle artifacts and optionally replay saved unsat proofs in Isabelle."
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        default="output_mirabelle",
        help="directory containing saved Mirabelle SMT artifacts",
    )
    parser.add_argument(
        "--mirabelle-log",
        default=None,
        help="path to mirabelle.log (defaults to OUTPUT_DIR/mirabelle.log if present)",
    )
    parser.add_argument(
        "--examples",
        type=int,
        default=5,
        help="number of example files to show per error kind",
    )
    parser.add_argument(
        "--skip-replay",
        action="store_true",
        help="do not run Isabelle replay on unsat proof outputs",
    )
    parser.add_argument(
        "--isabelle",
        default=None,
        help="path to Isabelle launcher (defaults to ./bin/isabelle if available)",
    )
    parser.add_argument(
        "--import-theory",
        default="HOL.SMT_CVC",
        help="theory import used for the temporary replay session",
    )
    parser.add_argument(
        "--replay-timeout",
        type=int,
        default=90,
        help="timeout in seconds for each proof replay inside a batch",
    )
    parser.add_argument(
        "--replay-selection",
        choices=["all", "one-per-goal"],
        default="all",
        help="which saved unsat proofs to replay",
    )
    parser.add_argument(
        "--replay-batch-size",
        type=int,
        default=100,
        help="number of proofs to replay per Isabelle batch build",
    )
    parser.add_argument(
        "--json",
        default=None,
        help="optional path for machine-readable JSON output",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    output_root = (Path(args.output_dir) if Path(args.output_dir).is_absolute() else repo_root / args.output_dir).resolve()
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

    replay_enabled = False
    if not args.skip_replay:
        isabelle_binary = Path(args.isabelle).resolve() if args.isabelle else default_isabelle_binary(repo_root)
        if isabelle_binary is None or not isabelle_binary.is_file():
            print(
                "skipping replay: no Isabelle binary found; pass --isabelle /path/to/bin/isabelle to enable it",
                file=sys.stderr,
            )
        else:
            replay_enabled = True
            replay_unsat_artifacts(
                repo_root=repo_root,
                artifacts=artifacts,
                log_entries=log_entries,
                isabelle_binary=isabelle_binary,
                import_theory=args.import_theory,
                replay_timeout=args.replay_timeout,
                replay_selection=args.replay_selection,
                replay_batch_size=args.replay_batch_size,
            )

    summary = render_summary(
        repo_root=repo_root,
        output_root=output_root,
        log_entries=log_entries,
        artifacts=artifacts,
        examples_per_kind=max(args.examples, 0),
        replay_enabled=replay_enabled,
    )
    sys.stdout.write(summary)

    if args.json:
        json_path = Path(args.json)
        if not json_path.is_absolute():
            json_path = repo_root / json_path
        json_path.write_text(
            json.dumps(json_payload(repo_root, log_entries, artifacts), indent=2, sort_keys=True),
            encoding="utf-8",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
