#!/bin/bash
trap "cd \"${PWD}\"" EXIT

#Submit solveAndCheck.sh to slurm for all .smt2 benchmarks in a directory (including subdirectories).
#All benchmarks are listed in a single benchmark_set_<name> file, every line becomes one call of solveAndCheck.sh.
#If evaluate.py saved the benchmarks a solver solved (prev_solved_<config>.txt in the input directory), the
#user is asked whether to run on all benchmarks or only on the previously solved ones. The latter submits one
#job per config, each on the benchmarks that config solved.

SUBMIT_JOB=${SUBMIT_JOB:-/barrett/scratch/local/bin/submit-job.sh}

#Defaults for options
partition="quad"
declare -a configs=()
solve_timeout=300
check_timeout=300
library=""
keep_str=""

Help()
{
   # Display Help
   echo "Run solveAndCheck.sh with slurm on all .smt2 files in a directory"
   echo "Usage: $0 [options] <input_dir ABSOLUTE PATH> <output_dir>"
   echo
   echo "options:"
   echo "p     Override partition (default $partition)"
   echo "c     Solver config (cvc5, verit, cpc, cvc5_solving, verit_solving). Can give several arguments with -c (default: cvc5 and verit)"
   echo "t     Set timeout for solving and producing proof (default $solve_timeout)"
   echo "T     Set timeout for reconstruction in Isabelle (default $check_timeout)"
   echo "l     Set library name (default: name of input_dir)"
   echo "k     Keep proofs, logs and a copy of the problem in each job's directory (default: delete them)"
   echo "h     Print this Help."
   echo
}

while getopts ":hkp:c:t:T:l:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      p) partition=$OPTARG;;
      c) configs+=("$OPTARG");;
      t) solve_timeout=$OPTARG;;
      T) check_timeout=$OPTARG;;
      l) library=$OPTARG;;
      k) keep_str="-k";;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit 1;;
   esac
done
shift $((OPTIND - 1))

if [[ "$#" -ne 2 ]]; then
  Help
  exit 1
fi

input_dir="${1%/}"
output_dir="${2%/}"

if ! [[ "$input_dir" =~ ^/ ]]; then
  echo "Error: input_dir has to be an absolute path"
  exit 1
fi
if ! [[ -d "$input_dir" ]]; then
  echo "Error: $input_dir is not a directory"
  exit 1
fi
if [[ -z "$library" ]]; then
  library=$(basename "$input_dir")
fi
if [[ ${#configs[@]} -eq 0 ]]; then
  configs=("cvc5" "verit")
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

#Do not mix results of different runs
if [[ -d "$output_dir" ]] && [[ -n "$(ls -A "$output_dir")" ]]; then
  echo "Error: $output_dir is not empty"
  exit 1
fi
mkdir -p "$output_dir"
output_dir=$(cd "$output_dir" && pwd)
cd "$output_dir"

#Submit one job array
#Arguments: benchmark file, results directory, configs
submit() {
  local bench_file=$1 results_dir=$2
  shift 2
  local job_configs=("$@")

  #Every job runs all configs one after the other, each can take up to solve + check timeout plus
  #10s each until timeout kills processes that ignore SIGTERM (kill_after in solveAndCheck.sh)
  local slurm_timeout=$(( ${#job_configs[@]} * (solve_timeout + check_timeout + 20) + 100 ))

  local config_str="" c
  for c in "${job_configs[@]}"; do
    config_str="$config_str -c $c"
  done
  local job_options="$keep_str$config_str -t $solve_timeout -T $check_timeout -l $library $input_dir"

  local name="solveAndCheck_${library}_$(IFS=_; echo "${job_configs[*]}")"
  echo "Submitting $name with $(wc -l < "$bench_file") benchmarks to partition $partition (slurm timeout ${slurm_timeout}s)"
  echo "  $SCRIPT_DIR/solveAndCheck.sh $job_options <benchmark>"

  local output
  output=$("$SUBMIT_JOB" --log-dirs --partition "$partition" --full-access-dir "$input_dir" -t $slurm_timeout -n "$name" -b "$bench_set_name" -d "$results_dir" -o "$job_options" "$SCRIPT_DIR/solveAndCheck.sh")
  if [[ $? -ne 0 ]]; then
    echo "ERROR: Slurm could not be called"
    echo "$output"
    exit 1
  fi
  echo "$output"
  echo "Send to slurm"
}

#Ask whether to run on all or on the previously solved benchmarks, if such lists exist
mode="a"
found_prev=false
for c in "${configs[@]}"; do
  [[ -f "$input_dir/prev_solved_$c.txt" ]] && found_prev=true
done
if [[ $found_prev == true ]]; then
  echo "Found lists of previously solved benchmarks in $input_dir:"
  for c in "${configs[@]}"; do
    prev_file="$input_dir/prev_solved_$c.txt"
    if [[ -f "$prev_file" ]]; then
      echo "  $c: $(wc -l < "$prev_file") benchmarks"
    else
      echo "  $c: no list"
    fi
  done
  while true; do
    read -r -p "Do you want to run on all benchmarks (a) or just on the previously solved ones (p)? " mode || exit 1
    [[ $mode == "a" || $mode == "p" ]] && break
  done
fi

if [[ $mode == "a" ]]; then
  #One line per benchmark
  bench_file="benchmark_set_$library"
  bench_set_name="$library"
  find "$input_dir" -type f -name "*.smt2" | sort > "$bench_file"
  if [[ ! -s "$bench_file" ]]; then
    echo "No benchmarks found in $input_dir"
    exit 1
  fi
  echo "Created $bench_file"
  submit "$bench_file" "Results" "${configs[@]}"
else
  #One job per config, each on the benchmarks this config solved before
  for c in "${configs[@]}"; do
    prev_file="$input_dir/prev_solved_$c.txt"
    if ! [[ -f "$prev_file" ]]; then
      echo "Skipping $c: no list of previously solved benchmarks"
      continue
    fi
    bench_file="benchmark_set_${library}_$c"
    bench_set_name="${library}_$c"
    #Only keep benchmarks that still exist
    while IFS= read -r bench; do
      [[ -f "$bench" ]] && echo "$bench"
    done < "$prev_file" > "$bench_file"
    if [[ ! -s "$bench_file" ]]; then
      echo "Skipping $c: no previously solved benchmarks"
      continue
    fi
    echo "Created $bench_file"
    submit "$bench_file" "Results_$c" "$c"
  done
fi
