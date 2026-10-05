#!/usr/bin/env bash
#
# DESCRIPTION: Run IsabelleCheckExternal's smt_check on the benchmark pair
# <rule>.smt2 / <rule>.alethe of every rule in a *-rules-list.txt file.
# The benchmarks are expected next to the list file.

PRG="$(basename "$0")"
SCRIPT_DIR="$(cd -P -- "$(dirname -- "$0")" && pwd)"
SMT_CHECK="$SCRIPT_DIR/../../IsabelleCheckExternal/lib/Tools/smt_check"

function usage() {
  echo
  echo "Usage: $PRG [-o declare_options] [-s smt_solver] [-t timeout] [-l log_dir] <rules-list.txt>"
  echo
  echo "  Runs smt_check on <rule>.smt2 and <rule>.alethe for each rule in <rules-list.txt>."
  echo "  Rules without both benchmark files are skipped."
  echo "  -o  declare options passed to smt_check (default: \"rare_rec_mode=1\")"
  echo "  -s  solver passed to smt_check (default: cvc5)"
  echo "  -t  timeout in seconds per rule (default: 300)"
  echo "  -l  directory for per-rule logs (default: ./smt_check_logs/<list name>)"
  echo "  -q  quiet run"
  echo
  exit 1
}

declare_options="rare_rec_mode=1"
solver=cvc5
timeout_s=300
log_dir=""
quiet_run=0

while getopts ":o:s:t:l:qh" option; do
  case ${option} in
    o) declare_options="${OPTARG}" ;;
    s) solver="${OPTARG}" ;;
    t) timeout_s="${OPTARG}" ;;
    l) log_dir="${OPTARG}" ;;
    q) quiet_run=1 ;;
    h) usage ;;
    \?) echo "Invalid option: -$OPTARG" >&2; usage ;;
    :) echo "Option -$OPTARG requires an argument." >&2; usage ;;
  esac
done
shift $((OPTIND - 1))

[ "$#" -ne 1 ] && usage
list="$1"
[ -f "$list" ] || { echo "$PRG: no such file: $list" >&2; exit 1; }
[ -x "$SMT_CHECK" ] || { echo "$PRG: smt_check not found or not executable: $SMT_CHECK" >&2; exit 1; }
[ -n "$ISABELLE_HOME" ] || { echo "$PRG: ISABELLE_HOME is not set" >&2; exit 1; }

bench_dir="$(cd -P -- "$(dirname -- "$list")" && pwd)"
[ -n "$log_dir" ] || log_dir="./smt_check_logs/$(basename "$list" .txt)"
mkdir -p "$log_dir"
log_dir="$(cd -P -- "$log_dir" && pwd)"

# smt_check writes its scratch theory into the working directory
work_dir="$(mktemp -d)"
trap 'rm -rf "$work_dir"' EXIT

passed=(); failed=(); skipped=()

while read -r rule; do
  [ -z "$rule" ] && continue
  smt2="$bench_dir/$rule.smt2"
  proof="$bench_dir/$rule.alethe"
  if [ ! -f "$smt2" ] || [ ! -f "$proof" ]; then
    if [ $quiet_run -eq 0 ]; then
      echo "SKIP  $rule (no benchmark)"
    fi
    skipped+=("$rule")
    continue
  fi

  log="$log_dir/$rule.log"
  (cd "$work_dir" && timeout "$timeout_s" "$SMT_CHECK" -s "$solver" -o "$declare_options" \
    -i "$smt2" -p "$proof") > "$log" 2>&1
  status=$?

  # smt_check always exits 0, so errors are detected from Isabelle's "***" output
  if [ $status -eq 124 ]; then
    if [ $quiet_run -eq 0 ]; then
      echo "FAIL  $rule (timeout after ${timeout_s}s, see $log)"
    fi
    failed+=("$rule")
  elif [ $status -ne 0 ] || grep -q '^\*\*\*' "$log"; then
    if [ $quiet_run -eq 0 ]; then
      echo "FAIL  $rule (see $log)"
    fi
    failed+=("$rule")
  else
    if [ $quiet_run -eq 0 ]; then
      echo "PASS  $rule"
    fi
    passed+=("$rule")
  fi
done < "$list"

if [ $quiet_run -eq 0 ]; then
  echo
fi
echo "passed: ${#passed[@]}  failed: ${#failed[@]}  skipped: ${#skipped[@]}"
for r in "${failed[@]}"; do echo "  failed: $r"; done

[ ${#failed[@]} -eq 0 ]
