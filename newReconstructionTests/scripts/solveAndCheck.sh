#!/bin/bash

#Solve a benchmark and immediately reconstruct the proof in Isabelle.
#Prints one line "RESULT_JSON: {...}" per solver config to stdout, everything else goes to stderr.
#Proofs and spy files are written to the current (slurm job) directory and are not cleaned up here.

#Binaries (can be overridden from the environment for local testing)
#CVC5_HOME=${CVC5_HOME:-~/Sources/cvc5/build/bin/cvc5}
CVC5_HOME=${CVC5_HOME:-/barrett/scratch/lachnitt/Binaries/cvc5/build/bin/cvc5}
VERIT_HOME=${VERIT_HOME:-/barrett/scratch/lachnitt/Binaries/verit/veriT}
ISABELLE_PATH=${ISABELLE_PATH:-/barrett/scratch/lachnitt/Binaries/dist-Isabelle_24-Sep-2026/Isabelle_24-Sep-2026/bin/isabelle}
export USER_HOME=${USER_HOME:-/barrett/scratch/lachnitt/Binaries/IsabelleSetUp/}

#Defaults for options
declare -a configs=("cvc5" "verit")
override_configs=false
solve_timeout=300
check_timeout=350
declare_options=""
library="N/A"

Help()
{
   # Display Help
   echo "Run a solver on a benchmark and reconstruct the proof with Isabelle smt_check"
   echo "Usage: $0 [options] <base_dir> <benchmark.smt2>"
   echo "base_dir is the benchmark folder, paths in the output are relative to it"
   echo
   echo "options:"
   echo "c     Solver config (cvc5, verit, cpc, cvc5_solving, verit_solving). Can give several arguments with -c (default: cvc5 and verit)"
   echo "t     Set timeout for solving and producing proof (default $solve_timeout)"
   echo "T     Set timeout for reconstruction in Isabelle (default $check_timeout)"
   echo "o     Set declare options for smt_check"
   echo "l     Set library name"
   echo "h     Print this Help."
   echo
}

while getopts ":hc:t:T:o:l:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      c)
      # On first -c, clear default array
      if [ "$override_configs" = false ]; then
        configs=()
        override_configs=true
      fi
      configs+=("$OPTARG")
      ;;
      t) solve_timeout=$OPTARG;;
      T) check_timeout=$OPTARG;;
      o) declare_options=$OPTARG;;
      l) library=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option" >&2
         exit 1;;
   esac
done
shift $((OPTIND - 1))

if [[ "$#" -ne 2 ]]; then
  Help >&2
  exit 1
fi

if ! [[ -d "$1" ]]; then
  echo "Error: $1 is not a directory" >&2
  exit 1
fi
input_dir=$(realpath "$1")

#Benchmark metadata. A relative benchmark path is interpreted relative to base_dir
input_file=$2
if ! [[ "$input_file" =~ ^/ ]]; then
  input_file="$input_dir/$input_file"
fi
if ! [[ -f "$input_file" ]]; then
  echo "Error: benchmark $input_file not found" >&2
  exit 1
fi
input_file=$(realpath "$input_file")
path="${input_file#$input_dir/}"
raw_name=$(basename -- "$input_file")
raw_name="${raw_name%.*}"

declare_options_str=()
if ! [[ -z "$declare_options" ]]; then
  declare_options_str=(-o "$declare_options")
fi

#------------------------------------------------------------------------------------
#-------------------------------------Solving----------------------------------------
#------------------------------------------------------------------------------------

#Sets: proof_file, proof_producing, solving_outcome, solving_status, solving_time, nr_of_lines
solve() {
  local config=$1
  local stderr_file="${raw_name}_${config}.stderr"
  proof_file="${raw_name}_${config}.alethe"
  proof_producing=1
  nr_of_lines=""

  local cmd
  case "$config" in
    cvc5)
      cmd=("$CVC5_HOME" --proof-prune-input --proof-mode=full-proof-strict --proof-format-mode=alethe --dump-proofs --produce-proofs --proof-granularity=dsl-rewrite --proof-alethe-define-skolems --proof-elim-subtypes --full-saturate-quant --no-stats --sat-random-seed=1 --lang=smt2 "$input_file");;
    cpc)
      proof_file="${raw_name}_${config}.proof"
      cmd=("$CVC5_HOME" --proof-prune-input --proof-mode=full-proof-strict --proof-format-mode=cpc --dump-proofs --produce-proofs --proof-granularity=dsl-rewrite --proof-elim-subtypes --full-saturate-quant --no-stats --sat-random-seed=1 --lang=smt2 "$input_file");;
    verit)
      cmd=("$VERIT_HOME" --print-cvc5-numbers --proof=- --proof-prune --proof-merge --proof-define-skolems --disable-banner --proof-with-sharing -s "$input_file");;
    cvc5_solving)
      proof_producing=0
      cmd=("$CVC5_HOME" --full-saturate-quant --no-stats --sat-random-seed=1 --lang=smt2 "$input_file");;
    verit_solving)
      proof_producing=0
      cmd=("$VERIT_HOME" --disable-banner -s "$input_file");;
    *)
      echo "Error: invalid solver config $config" >&2
      return 1;;
  esac

  if ! [[ -x "${cmd[0]}" ]]; then
    echo "Error: solver binary ${cmd[0]} for config $config not found" >&2
    return 1
  fi

  local start_time end_time
  start_time=$(date +%s%N)
  timeout "$solve_timeout" "${cmd[@]}" < /dev/null > "$proof_file" 2> "$stderr_file"
  local return_value=$?
  end_time=$(date +%s%N)
  solving_time=$((end_time - start_time))
  local first_line
  first_line=$(head -n 1 "$proof_file")
  if [ $return_value -eq 124 ]; then
    solving_outcome=-1
    solving_status="timeout"
  elif ! [ $return_value -eq 0 ] || ! [ -s "$proof_file" ]; then
    solving_outcome=-1
    solving_status="error"
  elif [[ $first_line == *"unknown"* ]]; then
    solving_outcome=-3
    solving_status="unknown"
  elif grep -q "(error " "$proof_file" "$stderr_file"; then
    solving_outcome=-4
    solving_status="error"
  elif [[ $first_line == "sat"* ]]; then
    solving_outcome=-2
    solving_status="sat"
  else
    solving_outcome=0
    solving_status="unsat"
    if [[ $proof_producing -eq 1 ]]; then
      nr_of_lines=$(grep -c -E "^\((assume|step|anchor)" "$proof_file") # ignore define-fun
    fi
  fi
}

#------------------------------------------------------------------------------------
#-------------------------------------Checking---------------------------------------
#------------------------------------------------------------------------------------

#Read a tuple printed by Isabelle that may be split across lines, e.g.
#   ("RESULT_CODE",
#    0) (line 126 of "...")
#Reads continuation lines from stdin until the closing paren and joins them.
read_tuple() {
  local tuple=$1 cont_line
  while [[ "$tuple" != *")"* ]]; do
    IFS= read -r cont_line || break
    tuple="$tuple $cont_line"
  done
  echo "$tuple"
}

#Sets: checking_outcome, checking_status, checking_time, error_rule, error_msg
check() {
  local config=$1
  local log_file="${raw_name}_${config}_isabelle.log"
  export ISABELLE_SMT_CVC_SPY="${PWD}/${raw_name}_${config}_spy.txt"
  checking_outcome=10
  error_rule=""
  error_msg=""

  local start_time end_time
  start_time=$(date +%s%N)
  timeout "$check_timeout" "$ISABELLE_PATH/isabelle" smt_check "${declare_options_str[@]}" -s "$config" -i "$input_file" -p "$proof_file" < /dev/null > "$log_file" 2>&1
  local return_value=$?
  end_time=$(date +%s%N)
  checking_time=$((end_time - start_time))

  local line tuple tmp
  while IFS= read -r line; do
    case "$line" in
      '("RESULT_CODE"'*)
        tuple=$(read_tuple "$line")
        checking_outcome=$(echo "$tuple" | grep -oP '"RESULT_CODE",\s*\K-?\d+')
        ;;
      '("RESULT_MSG"'*)
        tuple=$(read_tuple "$line")
        error_msg=$(echo "$tuple" | grep -oP '"RESULT_MSG",\s*"\K.*?(?="\))' | tr -s '[:space:]' ' ' | sed 's/ *$//')
        line="$tuple"
        ;;
    esac
    if [[ -z "$error_rule" && "$line" == *"Error replaying step"* ]]; then
      tmp="${line#*Error replaying step }"
      tmp="${tmp#"${tmp%%[![:space:]]*}"}"
      error_rule="${tmp%%[,)\"[:space:]]*}"
    fi
  done < "$log_file"

  #Codes are set in IsabelleCheckExternal/ML/smt_check_external.ML
  case "$checking_outcome" in
    0) checking_status="success";;
    1) checking_status="isabelle_error";;
    2) checking_status="unknown_type";;
    3) checking_status="bad_term";;
    4|5) checking_status="parse_error";;
    6) checking_status="replay_error";;
    7) checking_status="replay_timeout";;
    *) if [ $return_value -eq 124 ]; then checking_status="timeout"; else checking_status="no_result"; fi;;
  esac
}

#------------------------------------------------------------------------------------
#-------------------------------------Main-------------------------------------------
#------------------------------------------------------------------------------------

failed=0
for config in "${configs[@]}"; do
  if ! solve "$config"; then
    failed=1
    continue
  fi

  #Times are given in seconds, rounded to milliseconds
  solving_json=$(jq -cn --arg s "$solving_status" --argjson o "$solving_outcome" --argjson t "$solving_time" \
    --arg n "$nr_of_lines" \
    '{status: $s, outcome: $o, time_s: (($t / 1e6 | round) / 1e3)}
     + (if $n == "" then {} else {nr_of_lines: ($n | tonumber)} end)')

  checking_json='{"status":"skipped"}'
  if [[ $solving_outcome -eq 0 ]] && [[ "$config" == "cvc5" || "$config" == "verit" ]]; then
    check "$config"
    checking_json=$(jq -cn --arg s "$checking_status" --argjson o "$checking_outcome" --argjson t "$checking_time" \
      --arg r "$error_rule" --arg m "$error_msg" \
      '{status: $s, outcome: $o, time_s: (($t / 1e6 | round) / 1e3)}
       + (if $r == "" then {} else {error_rule: $r} end)
       + (if $m == "" then {} else {error_msg: $m} end)')
  fi

  result=$(jq -cn --arg b "$raw_name" --arg p "$input_file" --arg rp "$path" --arg l "$library" --arg c "$config" \
    --argjson solving "$solving_json" --argjson checking "$checking_json" \
    '{benchmark_name: $b, benchmark_path: $p, relative_benchmark_path: $rp, library_name: $l, config: $c,
      solving: $solving, checking: $checking}')
  echo "RESULT_JSON: $result"
done

exit $failed
