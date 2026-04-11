#!/usr/bin/env python3

from __future__ import annotations

import argparse
import collections
import dataclasses
import re
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path


ARTIFACT_RE = re.compile(
    r"^(?P<base>prob_(?P<line>\d{5})_(?P<offset>\d{6}))__(?P<serial>\d+)\.smt_(?P<kind>in|out)$"
)
RESULT_CODE_RE = re.compile(r'\("RESULT_CODE",\s*(-?\d+)\)')
RESULT_MSG_RE = re.compile(r'\("RESULT_MSG",\s*"([^"]*)"\)', re.DOTALL)
THEORY_NAME = "Check_SMT_Direct_Bench"


@dataclasses.dataclass(frozen=True)
class ProblemRef:
    session: str
    theory: str
    base: str


@dataclasses.dataclass
class Case:
    ref: ProblemRef
    in_path: Path
    out_path: Path


@dataclasses.dataclass
class Result:
    case: Case
    elapsed_seconds: float
    result_code: int | None
    result_msg: str | None
    detail: str | None
    timed_out: bool


def relpath(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def resolve_path(repo_root: Path, path_text: str) -> Path:
    path = Path(path_text)
    return path.resolve() if path.is_absolute() else (repo_root / path).resolve()


def default_output_dir(repo_root: Path) -> Path:
    extracted = repo_root / "output_mirabelle_zip_extract" / "output_mirabelle"
    if extracted.is_dir():
        return extracted
    return repo_root / "output_mirabelle"


def theory_from_dir(dirname: str) -> str:
    return re.sub(r"^\d+_", "", dirname)


def parse_artifact(path: Path) -> tuple[ProblemRef, int, str] | None:
    match = ARTIFACT_RE.match(path.name)
    if match is None:
        return None
    ref = ProblemRef(
        session=path.parent.parent.name,
        theory=theory_from_dir(path.parent.name),
        base=match.group("base"),
    )
    return ref, int(match.group("serial")), match.group("kind")


def is_proof_output(path: Path) -> bool:
    lines = path.read_text(errors="replace").splitlines()
    return len(lines) > 1 and lines[0].strip() == "unsat"


def collect_cases(output_root: Path) -> list[Case]:
    inputs: dict[ProblemRef, list[tuple[int, Path]]] = collections.defaultdict(list)
    outputs: dict[ProblemRef, list[tuple[int, Path]]] = collections.defaultdict(list)

    for path in sorted(output_root.rglob("*.smt_in")):
        parsed = parse_artifact(path)
        if parsed is None:
            continue
        ref, serial, kind = parsed
        if kind == "in":
            inputs[ref].append((serial, path))

    for path in sorted(output_root.rglob("*.smt_out")):
        parsed = parse_artifact(path)
        if parsed is None:
            continue
        ref, serial, kind = parsed
        if kind == "out" and is_proof_output(path):
            outputs[ref].append((serial, path))

    cases: list[Case] = []
    for ref, grouped_outputs in sorted(outputs.items(), key=lambda item: (item[0].session, item[0].theory, item[0].base)):
        grouped_inputs = sorted(inputs.get(ref, []))
        unused_inputs = set(range(len(grouped_inputs)))

        for out_serial, out_path in sorted(grouped_outputs):
            candidate_indices = [i for i in unused_inputs if grouped_inputs[i][0] <= out_serial]
            if candidate_indices:
                chosen = max(candidate_indices, key=lambda i: grouped_inputs[i][0])
            elif unused_inputs:
                chosen = min(unused_inputs, key=lambda i: abs(grouped_inputs[i][0] - out_serial))
            elif grouped_inputs:
                chosen = min(range(len(grouped_inputs)), key=lambda i: abs(grouped_inputs[i][0] - out_serial))
            else:
                continue

            unused_inputs.discard(chosen)
            _, in_path = grouped_inputs[chosen]
            cases.append(Case(ref=ref, in_path=in_path, out_path=out_path))

    return cases


def parse_result(output: str) -> tuple[int | None, str | None]:
    code_match = RESULT_CODE_RE.search(output)
    msg_match = RESULT_MSG_RE.search(output)
    code = int(code_match.group(1)) if code_match else None
    msg = msg_match.group(1).replace("\n", " ").strip() if msg_match else None
    return code, msg


def parse_status_code_partial(code: int | None) -> str:
    # Intentionally incomplete: only a few frequent result codes are explained.
    if code == 0:
        return "success"
    if code == 1:
        return "checker_error"
    if code == 2:
        return "unknown_smt_type"
    if code == 3:
        return "bad_smt_term"
    if code == 4:
        return "smtlib_parse_error"
    if code == 5:
        return "parse_or_solver_error"
    if code == 6:
        return "replay_error"
    if code == 7:
        return "timeout_or_interrupt"
    return "unknown"


def shorten(text: str | None, limit: int = 220) -> str | None:
    if text is None or len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def extract_detail(output: str) -> str | None:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    marked = [
        line
        for line in lines
        if line.startswith("***")
        or line.startswith("Error ")
        or "At command" in line
        or "raised" in line
    ]
    if marked:
        return " || ".join(marked[-4:])
    plain = [
        line
        for line in lines
        if "RESULT_MSG" not in line
        and "RESULT_CODE" not in line
        and not line.startswith("Output (line ")
        and not line.startswith("Draft: theory ")
    ]
    if plain:
        return " || ".join(plain[-4:])
    return None


def theory_text(case: Case) -> str:
    in_path = str(case.in_path).replace("\\", "\\\\").replace('"', '\\"')
    out_path = str(case.out_path).replace("\\", "\\\\").replace('"', '\\"')
    return textwrap.dedent(
        f"""\
        theory {THEORY_NAME}
          imports Main "HOL.SMT_CVC"
        begin

        declare [[smt_trace=true, smt_verbose=true]]

        check_smt ("cvc5_proof")
          "{in_path}"
          "{out_path}"

        end
        """
    )


def run_case(repo_root: Path, isabelle: Path, case: Case, timeout_seconds: int) -> Result:
    with tempfile.TemporaryDirectory(prefix="check_smt_direct_") as tmp:
        theory_file = Path(tmp) / f"{THEORY_NAME}.thy"
        theory_file.write_text(theory_text(case), encoding="utf-8")

        command = [
            str(isabelle),
            "process_theories",
            "-d",
            str(repo_root / "src" / "HOL"),
            "-O",
            "-U",
            "-v",
            "-l",
            "HOL",
            "-f",
            str(theory_file),
            THEORY_NAME,
        ]

        started = time.perf_counter()
        try:
            completed = subprocess.run(
                command,
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=timeout_seconds + 300,
                check=False,
            )
            elapsed = time.perf_counter() - started
            output = completed.stdout + completed.stderr
            result_code, result_msg = parse_result(output)
            detail = None if result_code == 0 else shorten(extract_detail(output))
            return Result(
                case=case,
                elapsed_seconds=elapsed,
                result_code=result_code,
                result_msg=result_msg,
                detail=detail,
                timed_out=False,
            )
        except subprocess.TimeoutExpired as exc:
            elapsed = time.perf_counter() - started
            output = (exc.stdout or "") + (exc.stderr or "")
            result_code, result_msg = parse_result(output)
            return Result(
                case=case,
                elapsed_seconds=elapsed,
                result_code=result_code,
                result_msg=result_msg or f"timeout after {timeout_seconds + 300}s",
                detail=shorten(extract_detail(output)),
                timed_out=True,
            )


def matches(case: Case, needle: str | None) -> bool:
    if not needle:
        return True
    return any(
        needle in text
        for text in (
            case.ref.session,
            case.ref.theory,
            case.ref.base,
            str(case.in_path),
            str(case.out_path),
        )
    )


def print_result(index: int, total: int, result: Result, repo_root: Path) -> None:
    status = "timeout" if result.timed_out else ("ok" if result.result_code == 0 else "fail")
    fields = [
        f"[{index}/{total}]",
        status,
        f"{result.elapsed_seconds:.3f}s",
        f"result_code={result.result_code if result.result_code is not None else 'missing'}",
        f"status_hint={parse_status_code_partial(result.result_code)}",
        relpath(result.case.out_path, repo_root),
    ]
    if result.result_msg:
        fields.append(f"result_msg={result.result_msg}")
    if result.detail:
        fields.append(f"detail={result.detail}")
    print(" | ".join(fields))


def print_summary(results: list[Result]) -> None:
    total_seconds = sum(result.elapsed_seconds for result in results)
    ok = sum(result.result_code == 0 for result in results)
    failed = sum((result.result_code != 0) and not result.timed_out for result in results)
    timeout = sum(result.timed_out for result in results)

    print("")
    print(f"cases={len(results)}")
    print(f"ok={ok} fail={failed} timeout={timeout}")
    print(f"total_seconds={total_seconds:.3f}")
    if results:
        slowest = max(results, key=lambda result: result.elapsed_seconds)
        print(f"avg_seconds={total_seconds / len(results):.3f}")
        print(
            "slowest="
            f"{slowest.elapsed_seconds:.3f}s "
            f"{slowest.case.ref.session}/{slowest.case.ref.theory}/{slowest.case.ref.base}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Direct check_smt benchmark runner with richer error output.")
    parser.add_argument("output_dir", nargs="?", help="Mirabelle output directory")
    parser.add_argument("--limit", type=int, default=None, help="maximum number of cases")
    parser.add_argument("--match", default=None, help="only run matching cases")
    parser.add_argument("--timeout", type=int, default=120, help="timeout per case in seconds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    output_root = resolve_path(repo_root, args.output_dir) if args.output_dir else default_output_dir(repo_root)
    isabelle = repo_root / "bin" / "isabelle"

    if not isabelle.is_file():
        print(f"missing Isabelle launcher: {isabelle}", file=sys.stderr)
        return 2
    if not output_root.is_dir():
        print(f"output directory not found: {output_root}", file=sys.stderr)
        return 2

    cases = [case for case in collect_cases(output_root) if matches(case, args.match)]
    if args.limit is not None:
        cases = cases[: max(args.limit, 0)]
    if not cases:
        print(f"no proof-producing cases found in {output_root}", file=sys.stderr)
        return 1

    results: list[Result] = []
    for index, case in enumerate(cases, start=1):
        result = run_case(repo_root, isabelle, case, args.timeout)
        results.append(result)
        print_result(index, len(cases), result, repo_root)

    print_summary(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
