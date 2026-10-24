#!/usr/bin/env bash
# Evaluate an ML file in the context of the given theories (default Main), as
# `isabelle ML_process -l <session>` would, without the JVM: start Poly/ML with the command line
# isa-poly-setup.sh captured from a real ML_process run (the heap hierarchy of the session, the ML
# options, and the init evaluations of ML_process: Options.load_*default (),
# Resources.init_session_env () and Isabelle_Process.init* ()), with the environment ML_process
# gives it, and with the capture's own evaluation replaced by the given file. One theory is used
# as it is; several are merged into a fresh theory importing all of them.
#
# The settings environment comes from sourcing lib/scripts/getsettings, as bin/isabelle does.
# Poly/ML is exec'd, so this process becomes it: a `timeout` in front kills and reaps it, and GNU
# time counts its CPU time. (`isabelle env` gives the same environment, but runs its command as a
# child, and a timeout would kill the wrapper and orphan Poly/ML.)
#
# Two values of the capture belong to the host that made it and are replaced: --gcthreads becomes
# the number of cores this process may use (nproc), as ML_process would compute it here. And
# ISA_MAXHEAP (MB), if set and non-empty, adds --maxheap, so that a check needing more memory
# fails inside Isabelle (Interrupt_Breakdown) instead of the job being killed at its memory limit.
#
# Refuses to launch, with a message starting "isa-poly:" and exit code 3, if the capture is
# missing or not an ML_process command line, or, with ISA_REFUSE_QUICK_AND_DIRTY=true, if its
# options turn quick_and_dirty on.
#
# Usage: [USER_HOME=<dir>] [ISA_MAXHEAP=<MB>] isa-poly.sh <isabelle-home> <capture-dir> <tmp-dir> <ml-file> [<theory>...]
set -u
refuse() { echo "isa-poly: $*" >&2; exit 3; }
[ $# -ge 4 ] || refuse "usage: isa-poly.sh <isabelle-home> <capture-dir> <tmp-dir> <ml-file> [<theory>...]"
ISABELLE_HOME=$(cd "$1" 2>/dev/null && pwd) || refuse "no Isabelle tree at $1"
files=$(cd "$2" 2>/dev/null && pwd) || refuse "no capture at $2; run isa-poly-setup.sh"
tmp=$3
ml=$(realpath -e "$4" 2>/dev/null) || refuse "no ML file $4"
shift 4
theories=("$@")
[ ${#theories[@]} -gt 0 ] || theories=(Main)

set +u                                  # the settings scripts use unset variables
source "$ISABELLE_HOME/lib/scripts/getsettings" || refuse "cannot load the settings of $ISABELLE_HOME"
set -u

for f in argv options init_session env; do
  [ -s "$files/$f" ] || refuse "$files/$f is missing; run isa-poly-setup.sh"
done
if [ "${ISA_REFUSE_QUICK_AND_DIRTY:-false}" = true ]; then
  grep -qx 'QUICK_AND_DIRTY=false' "$files/env" \
    || refuse "quick_and_dirty is not off in the options of $files" \
         "($(grep '^QUICK_AND_DIRTY=' "$files/env" || echo 'no QUICK_AND_DIRTY line')); refusing"
fi

# The capture ends with ML_process's last init evaluation, then the setup's own: drop the latter.
mapfile -d '' -t argv < "$files/argv"
n=${#argv[@]}
[ "$n" -ge 5 ] && [ "${argv[n-4]}" = --eval ] && [[ "${argv[n-3]}" == 'Isabelle_Process.init'*' ()' ]] \
  && [ "${argv[n-2]}" = --eval ] \
  || refuse "$files/argv does not end in ML_process's Isabelle_Process.init* () and one evaluation"
argv=("${argv[@]:0:n-2}")
for i in "${!argv[@]}"; do
  [ "${argv[i]}" = --gcthreads ] && argv[i+1]=$(nproc)
done
[ -n "${ISA_MAXHEAP:-}" ] && argv=("${argv[0]}" --maxheap "$ISA_MAXHEAP" "${argv[@]:1}")

loader=Thy_Info
while IFS='=' read -r k v; do
  case $k in
    ML_HOME|ML_PLATFORM) export "$k=$v" ;;
    THEORY_LOADER) loader=$v ;;
  esac
done < "$files/env"
mkdir -p "$tmp" || refuse "cannot create $tmp"
export ISABELLE_PROCESS_OPTIONS=$files/options ISABELLE_INIT_SESSION=$files/init_session
export ISABELLE_TMP=$tmp POLYSTATSDIR=$tmp

thy_list=$(printf '"%s", ' "${theories[@]}"); thy_list=${thy_list%, }
main_eval="val thy =
  (case map $loader.get_theory [$thy_list] of
    [thy] => thy
  | thys => Theory.begin_theory (\"Fast_Check\", Position.none) thys);
val _ = Context.setmp_generic_context (SOME (Context.Theory thy))
  (fn () => ML_Context.eval_file ML_Compiler.flags (Path.explode \"$ml\")) ();"
exec "${argv[@]}" --eval "$main_eval" < /dev/null
