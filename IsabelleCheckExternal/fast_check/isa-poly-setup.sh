#!/usr/bin/env bash
# Capture, once per Isabelle tree and session, how `isabelle ML_process -l <session>` starts
# Poly/ML, so that isa-poly.sh can start it the same way for every check, without the JVM.
#
# ML_process is Isabelle/Scala: a JVM that computes the Poly/ML command line (the heap hierarchy
# of the session, the ML options, the init evaluations), writes the system options and the session
# resources to two files, and starts Poly/ML with environment variables naming them. Here the ML
# process a real ML_process starts copies all of that out, into <dest>:
#
#   argv          its own command line, NUL-separated (/proc/self/cmdline)
#   options       the system options (the file ISABELLE_PROCESS_OPTIONS names, YXML)
#   init_session  the session resources (the file ISABELLE_INIT_SESSION names, YXML)
#   env           ML_HOME and ML_PLATFORM as ML_process set them; QUICK_AND_DIRTY: Isabelle's
#                 own reading of that option in the captured options; THEORY_LOADER: the ML
#                 structure with get_theory in this tree (Thy_Info in older trees, Build in newer)
#
# quick_and_dirty lets Isabelle accept steps proved by cheat_tac (the replay's trust rule, the
# skip-proof tactics). It is recorded in env, and check.sh reports it with every result. With
# ISA_REFUSE_QUICK_AND_DIRTY=true the capture is refused if it is on.
#
# The files embed absolute paths of the Isabelle tree and of the user directory, so run this where
# the checks run, and again whenever the tree or its heaps change (check.sh does that itself).
#
# Usage: [USER_HOME=<dir>] isa-poly-setup.sh <isabelle-home> <dest> [<session> [<session-dir>...]]
set -euo pipefail
[ $# -ge 2 ] || { echo "usage: isa-poly-setup.sh <isabelle-home> <dest> [<session> [<session-dir>...]]" >&2; exit 2; }
isabelle_home=$1 dest=$2 session=${3:-HOL}
shift $(( $# < 3 ? $# : 3 ))
dirs=()
for d in "$@"; do dirs+=(-d "$d"); done
mkdir -p "$dest"
dest=$(cd "$dest" && pwd)
if [ -f "$isabelle_home/src/Pure/Thy/thy_info.ML" ]; then loader=Thy_Info; else loader=Build; fi
rm -f "$dest/argv" "$dest/options" "$dest/init_session" "$dest/env"
"$isabelle_home/bin/isabelle" ML_process "${dirs[@]}" -l "$session" -e "
let
  fun out name = Path.explode (\"$dest/\" ^ name);
  fun copy var name = Bytes.write (out name) (Bytes.read (Path.explode (getenv var)));
  val cmdline =
    let val s = BinIO.openIn \"/proc/self/cmdline\" in BinIO.inputAll s before BinIO.closeIn s end;
in
  Bytes.write (out \"argv\") (Bytes.string (Byte.bytesToString cmdline));
  copy \"ISABELLE_PROCESS_OPTIONS\" \"options\";
  copy \"ISABELLE_INIT_SESSION\" \"init_session\";
  Bytes.write (out \"env\") (Bytes.string (cat_lines
    [\"ML_HOME=\" ^ getenv \"ML_HOME\",
     \"ML_PLATFORM=\" ^ getenv \"ML_PLATFORM\",
     \"QUICK_AND_DIRTY=\" ^ Bool.toString (Options.default_bool \"quick_and_dirty\"),
     \"THEORY_LOADER=$loader\"] ^ \"\\n\"))
end"
for f in argv options init_session env; do
  [ -s "$dest/$f" ] || { echo "isa-poly-setup: $dest/$f was not written" >&2; exit 1; }
done
if [ "${ISA_REFUSE_QUICK_AND_DIRTY:-false}" = true ] && ! grep -qx 'QUICK_AND_DIRTY=false' "$dest/env"; then
  echo "isa-poly-setup: quick_and_dirty is on in the options ML_process passes" \
    "($(grep '^QUICK_AND_DIRTY=' "$dest/env")); refusing" >&2
  rm -f "$dest/argv" "$dest/options" "$dest/init_session" "$dest/env"
  exit 1
fi
echo "isa-poly-setup: wrote $dest (session: $session, poly: $(tr '\0' '\n' < "$dest/argv" | head -1), $(grep '^QUICK_AND_DIRTY=' "$dest/env"))"
