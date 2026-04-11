#!/usr/bin/env python3

from __future__ import annotations

import argparse
import collections
import dataclasses
import re
import subprocess
import sys
import time
from pathlib import Path


ARTIFACT_RE = re.compile(
    r"^(?P<base>prob_(?P<line>\d{5})_(?P<offset>\d{6}))__(?P<serial>\d+)\.smt_(?P<kind>in|out)$"
)
RESULT_CODE_RE = re.compile(r'\("RESULT_CODE",\s*(-?\d+)\)')
RESULT_MSG_RE = re.compile(r'\("RESULT_MSG",\s*"([^"]*)"\)', re.DOTALL)


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
    # TODO: I need to still make this better by looking at the artifact smt and giving more proper answer
    # I am not sure how to it
    if code == 0:
        return "success"
    if code == 5:
        return "parse_or_solver_error"
    if code == 6:
        return "replay_error"
    if code == 7:
        return "timeout_or_interrupt"
    return "unknown"


def run_case(repo_root: Path, isabelle: Path, case: Case, timeout_seconds: int) -> Result:
    command = [
        str(isabelle),
        "smt_check",
        "-i",
        str(case.in_path),
        "-p",
        str(case.out_path),
        str(timeout_seconds),
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
        result_code, result_msg = parse_result(completed.stdout + completed.stderr)
        return Result(
            case=case,
            elapsed_seconds=elapsed,
            result_code=result_code,
            result_msg=result_msg,
            timed_out=False,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - started
        result_code, result_msg = parse_result((exc.stdout or "") + (exc.stderr or ""))
        return Result(
            case=case,
            elapsed_seconds=elapsed,
            result_code=result_code,
            result_msg=result_msg or f"timeout after {timeout_seconds + 300}s",
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
    parser = argparse.ArgumentParser(description="Simple check_smt benchmark runner.")
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
