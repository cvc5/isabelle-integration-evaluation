#!/usr/bin/env bash
# The check of ../lib/Tools/smt_check without the JVM: Isabelle's Alethe replay on one SMT-LIB
# problem and one Alethe proof, in a Poly/ML process that isa-poly.sh starts from a capture of
# `isabelle ML_process -l <session>`. The check itself is isa-driver.ML (what check_smt2 does).
# The proof is checked as given (it must already be in the form the replay takes).
#
# Usage: check.sh [-d dir] [-l session] [-t theory] [-s solver] [-o declare_options] -i <smt2_problem> -p <alethe_proof> [timeout]
#   The options are those of smt_check: -l the session (default SMTCheckExternal), -t a theory to
#   import besides SMTCheckExternal.SMT_Check_External (it must be in the session's heap, e.g.
#   Complex_Main), -s the solver (cvc5, the default, replays as cvc5_proof), -o the declare
#   options, e.g. "rare_rec_mode=2, smt_nat_as_int=false". [timeout] sets ISA_TIMEOUT.
#
# The first check builds the session if its heap is missing (with the JVM) and captures the
# Poly/ML start in $ISABELLE_HOME_USER/smt_check_poly/<session>; the capture is made again when the
# heap is newer. Rebuild the heap yourself after changing ../ML (isabelle build -b SMTCheckExternal).
#
# Output, on stdout:
#   ("RESULT_MSG", "...") and ("RESULT_CODE", n): as smt_check prints them (codes in isa-driver.ML)
#   [cfg isabelle] rc= time= cpu= result= code= replay_s= rss_kb= replay= qd=
#     result: checked | error (replay or type error) | parse-error | timeout | memout (out of
#     Poly/ML heap) | stack (out of Poly/ML stack) | crash (an exception check_smt lets escape) |
#     refused (isa-poly.sh would not launch); code: isa-driver.ML's; replay_s: the replay alone,
#     timed in ML; time is wall-clock, cpu user+sys and rss_kb the maximum, from GNU time;
#     qd: whether quick_and_dirty was on
#   === stderr isabelle ===  on failure: the message, the failing step and its rule, stderr
# Exit status 0 if Isabelle checked the proof, 1 if not, 2 if the inputs or the set-up are missing.
#
# Environment:
#   ISABELLE_HOME              the Isabelle tree (required, as for smt_check)
#   ISA_TIMEOUT                the whole process (wall seconds, default 900)
#   ISA_SMT_TIMEOUT            smt_timeout and the per-step limit of the replay (seconds; default:
#                              unset, Isabelle's own values as in smt_check)
#   ISA_RARE_MODE              rare_rec_mode (default: unset, Isabelle's own value)
#   ISA_TRACE                  smt_trace, true | false (default: unset); prints every goal
#   ISA_MAXHEAP                Poly/ML heap cap (MB, default 9000; "" for none)
#   ISA_REFUSE_QUICK_AND_DIRTY true: refuse to check if quick_and_dirty is on (default false)
#   KEEP_WORK=<dir>            keeps the work directory (problem, proof, Isabelle's output)

usage() {
  sed -n '7,11p' "$0" | cut -c3- >&2
  exit 2
}

here=$(dirname "$(readlink -f "$0")")
dirs=()
session=SMTCheckExternal
theories=(SMTCheckExternal.SMT_Check_External)
solver=cvc5
declare_options=""
PROBLEM="" PROOF=""
while getopts ":d:l:o:s:p:i:t:" option; do
  case $option in
    d) dirs+=("$OPTARG") ;;
    l) session=$OPTARG ;;
    t) [ -n "$OPTARG" ] && theories+=("$OPTARG") ;;
    i) PROBLEM=$OPTARG ;;
    p) PROOF=$OPTARG ;;
    s) solver=$OPTARG ;;
    o) declare_options=$OPTARG ;;
    \?) echo "check: invalid option -$OPTARG" >&2; usage ;;
    :) echo "check: option -$OPTARG requires an argument" >&2; usage ;;
  esac
done
shift $((OPTIND - 1))
[ -n "${1:-}" ] && ISA_TIMEOUT=$1
[ -n "$PROBLEM" ] && [ -n "$PROOF" ] || usage
[ "$solver" = cvc5 ] && solver=cvc5_proof

[ -n "${ISABELLE_HOME:-}" ] || { echo "check: ISABELLE_HOME is not set" >&2; exit 2; }
isabelle=$ISABELLE_HOME/bin/isabelle
ISA_DRIVER=${ISA_DRIVER:-$here/isa-driver.ML}
ISA_POLY=${ISA_POLY:-$here/isa-poly.sh}
ISA_TIMEOUT=${ISA_TIMEOUT:-900}
ISA_SMT_TIMEOUT=${ISA_SMT_TIMEOUT:-}
ISA_RARE_MODE=${ISA_RARE_MODE:-}
ISA_TRACE=${ISA_TRACE:-}
ISA_MAXHEAP=${ISA_MAXHEAP-9000}
export ISABELLE_HOME ISA_MAXHEAP

[ -r "$PROBLEM" ] || { echo "check: cannot read $PROBLEM" >&2; exit 2; }
[ -r "$PROOF" ] || { echo "check: cannot read $PROOF" >&2; exit 2; }

# the session directory, unless IsabelleCheckExternal is already a component (as smt_check makes it)
if ! "$isabelle" components -l | grep -qF 'IsabelleCheckExternal'; then
  dirs+=("$(cd -P -- "$here/.." && pwd)")
fi
dir_args=()
for d in "${dirs[@]}"; do dir_args+=(-d "$d"); done

# the heap (built once if missing) and the capture of the Poly/ML start (made again if older)
#(ML_IDENTIFIER, the heaps' subdirectory, is only set inside ML_process: take the heap from the
# capture's heap hierarchy, and before the first capture look for it with ML_SYSTEM)
mapfile -t env_vals < <("$isabelle" getenv -b ISABELLE_HEAPS ISABELLE_HEAPS_SYSTEM ML_SYSTEM ISABELLE_HOME_USER)
ISA_POLY_FILES=${ISA_POLY_FILES:-${env_vals[3]}/smt_check_poly/$session}
heap=""
if [ -s "$ISA_POLY_FILES/argv" ]; then
  heap=$(tr '\0' '\n' < "$ISA_POLY_FILES/argv" | grep -m1 -oP 'loadHierarchy \[.*"\K[^"]+(?="\])')
  [ -f "$heap" ] || heap=""
fi
if [ -z "$heap" ]; then
  for h in "${env_vals[0]}" "${env_vals[1]}"; do
    for f in "$h/${env_vals[2]}"_*/"$session"; do [ -f "$f" ] && { heap=$f; break 2; }; done
  done
fi
if [ -z "$heap" ]; then
  echo "check: no $session heap, building it" >&2
  "$isabelle" build "${dir_args[@]}" -b "$session" >&2 || { echo "check: building $session failed" >&2; exit 2; }
  recapture=true
fi
if [ -n "${recapture:-}" ] || ! [ -s "$ISA_POLY_FILES/argv" ] || [ "$heap" -nt "$ISA_POLY_FILES/argv" ]; then
  # into a fresh directory first, so that checks running in parallel never see half a capture
  mkdir -p "$(dirname "$ISA_POLY_FILES")"
  new=$(mktemp -d "$ISA_POLY_FILES.XXXXXX")
  if "$here/isa-poly-setup.sh" "$ISABELLE_HOME" "$new" "$session" "${dirs[@]}" >&2; then
    old=$ISA_POLY_FILES.old.$$
    { [ -e "$ISA_POLY_FILES" ] && mv -T "$ISA_POLY_FILES" "$old"; mv -T "$new" "$ISA_POLY_FILES"; } 2>/dev/null
    rm -rf "$old" "$new"
  else
    rm -rf "$new"
  fi
fi
if ! [ -s "$ISA_POLY_FILES/argv" ]; then
  echo "check: no Poly/ML capture in $ISA_POLY_FILES; run isa-poly-setup.sh $ISABELLE_HOME $ISA_POLY_FILES $session" >&2
  exit 2
fi
qd=$(grep -oP '^QUICK_AND_DIRTY=\K.*' "$ISA_POLY_FILES/env")

ulimit -s unlimited 2>/dev/null || true
PROBLEM=$(readlink -f "$PROBLEM"); PROOF=$(readlink -f "$PROOF")
work=$(mktemp -d "${TMPDIR:-/tmp}/cisa.XXXXXX")
if [ -n "${KEEP_WORK:-}" ]; then
  trap 'mkdir -p "$KEEP_WORK" && rm -rf "$KEEP_WORK/$(basename "$PROOF")" && mv "$work" "$KEEP_WORK/$(basename "$PROOF")"' EXIT
else
  trap 'rm -rf "$work"' EXIT
fi
cd "$work" || exit 2
# the queries after check-sat are not part of what is checked, and the reader chokes on some
sed -e '/^[[:space:]]*(get-unsat-core)[[:space:]]*$/d' \
    -e '/^[[:space:]]*(get-unsat-assumptions)[[:space:]]*$/d' \
    -e '/^[[:space:]]*(get-proof)[[:space:]]*$/d' \
    -e '/^[[:space:]]*(get-model)[[:space:]]*$/d' "$PROBLEM" > problem.smt2
# Isabelle wants the solver's `unsat` before the proof
if [ "$(head -n1 "$PROOF")" = unsat ]; then cp "$PROOF" proof.alethe
else { echo unsat; cat "$PROOF"; } > proof.alethe; fi

timed() { # <statfile> <cmd...>
  local f=$1; shift
  if [ -x /usr/bin/time ]; then
    /usr/bin/time -f '%e %U %S %M' -o "$f" "$@"
  else
    local t0 t1 rc
    t0=$(date +%s.%N); "$@"; rc=$?; t1=$(date +%s.%N)
    awk -v a="$t0" -v b="$t1" 'BEGIN{printf "%.3f 0 0 0\n", b-a}' > "$f"
    return $rc
  fi
}
wall() { awk 'END{printf "%.3f", $1}' "$1" 2>/dev/null; }
cpu() { awk 'END{printf "%.3f", $2+$3}' "$1" 2>/dev/null; }
rss() { awk 'END{print $4+0}' "$1" 2>/dev/null; }
ml_string() { local s=${1//\\/\\\\}; s=${s//\"/\\\"}; printf '"%s"' "$s"; }
ml_opt() { [ -n "$1" ] && printf '(SOME %s)' "$1" || printf NONE; }

# the check: isa-driver.ML, then the call with this pair and the limits
smt_timeout=""; [ -n "$ISA_SMT_TIMEOUT" ] && smt_timeout=$ISA_SMT_TIMEOUT.0
{ cat "$ISA_DRIVER"
  printf 'val _ = isa_check %s %s %s %s %s %s %s;\n' "$(ml_string "$solver")" \
    "$(ml_string "$work/problem.smt2")" "$(ml_string "$work/proof.alethe")" \
    "$(ml_opt "$smt_timeout")" "$(ml_opt "$ISA_RARE_MODE")" "$(ml_opt "$ISA_TRACE")" \
    "$(ml_string "$declare_options")"; } > check.ML
# isa-poly.sh execs Poly/ML: timeout kills and reaps it, and GNU time counts its CPU
timed isa.stat timeout -k 10 "$ISA_TIMEOUT" "$ISA_POLY" "$ISABELLE_HOME" "$ISA_POLY_FILES" \
  "$work/isatmp" "$work/check.ML" "${theories[@]}" > isa.out 2> isa.err
isa_rc=$?
code=$(grep -oE '^ISA_RESULT_CODE [0-9a-z]+' isa.out | tail -1 | awk '{print $2}')
replay_s=$(grep -oE 'REPLAY_TIME [0-9.]+' isa.out | awk '{print $2}')
if [ "$isa_rc" -eq 124 ] || [ "$isa_rc" -eq 137 ]; then isa_result=timeout
elif grep -q '^isa-poly: ' isa.err; then isa_result=refused
elif grep -q 'Unable to increase stack' isa.out isa.err; then isa_result=stack
elif [ "$code" = memout ] || { { [ -z "$code" ] || [ "$code" = crash ]; } \
        && grep -q 'Interrupt_Breakdown' isa.out isa.err; }; then isa_result=memout
elif [ -z "$code" ] || [ "$code" = crash ]; then isa_result=crash
elif [ "$code" = 0 ]; then isa_result=checked
elif [ "$code" = 7 ]; then isa_result=timeout       # smt_timeout inside a step
elif [ "$code" -ge 2 ] && [ "$code" -le 5 ]; then isa_result=parse-error
else isa_result=error; fi                            # 1: replay/type error, 6: replay error
grep -E '^\("RESULT_(MSG|CODE)", ' isa.out
echo "[cfg isabelle] rc=$isa_rc time=$(wall isa.stat) cpu=$(cpu isa.stat) result=$isa_result code=${code:-none} replay_s=${replay_s:-0} rss_kb=$(rss isa.stat) replay=$solver qd=$qd"
if [ "$isa_result" != checked ]; then
  echo "=== stderr isabelle ==="
  msg=$(grep -m1 '^ISA_RESULT_MSG ' isa.out | cut -c16- | tr -s ' ' | cut -c1-600)
  echo "msg: $msg"
  step=$(echo "$msg" | grep -oE 'in step [^ ]+' | head -1 | awk '{print $3}')
  if [ -n "$step" ]; then
    echo "step: $(grep -m1 -E "^\(step $step " proof.alethe | grep -oE ':rule [^ )]+')"
    grep -m1 -E "^\(step $step " proof.alethe | head -c 600; echo
  fi
  grep -E '^\*\*\*|^Exception-|exception' isa.out isa.err | grep -v RESULT_MSG | head -5 | cut -c1-400
  head -c 1000 isa.err; echo
  exit 1
fi
exit 0
