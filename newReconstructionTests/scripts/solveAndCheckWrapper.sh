#!/bin/bash
trap "cd \"${PWD}\"" EXIT

#Submit solveAndCheck.sh to slurm for all .smt2 benchmarks in a directory (including subdirectories).
#All benchmarks are listed in a single benchmark_set_<name> file, every line becomes one call of solveAndCheck.sh.

SUBMIT_JOB=${SUBMIT_JOB:-/barrett/scratch/local/bin/submit-job.sh}

#Defaults for options
partition="quad"
declare -a configs=()
solve_timeout=300
check_timeout=600
library=""
cleanup_str=""

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
   echo "r     Remove proofs and logs after each benchmark"
   echo "h     Print this Help."
   echo
}

while getopts ":hrp:c:t:T:l:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      p) partition=$OPTARG;;
      c) configs+=("$OPTARG");;
      t) solve_timeout=$OPTARG;;
      T) check_timeout=$OPTARG;;
      l) library=$OPTARG;;
      r) cleanup_str="-r";;
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

#One line per benchmark
bench_file="benchmark_set_$library"
find "$input_dir" -type f -name "*.smt2" | sort > "$bench_file"
nr_benchs=$(wc -l < "$bench_file")
if [[ $nr_benchs -eq 0 ]]; then
  echo "No benchmarks found in $input_dir"
  exit 1
fi
echo "Created $bench_file with $nr_benchs benchmarks"

#Every job runs all configs one after the other, each can take up to solve + check timeout
slurm_timeout=$(( ${#configs[@]} * (solve_timeout + check_timeout) + 100 ))

config_str=""
for c in "${configs[@]}"; do
  config_str="$config_str -c $c"
done
job_options="$cleanup_str$config_str -t $solve_timeout -T $check_timeout -l $library $input_dir"

name="solveAndCheck_${library}_$(IFS=_; echo "${configs[*]}")"
echo "Submitting $name to partition $partition (slurm timeout ${slurm_timeout}s)"
echo "  $SCRIPT_DIR/solveAndCheck.sh $job_options <benchmark>"

output=$("$SUBMIT_JOB" --log-dirs --partition "$partition" --full-access-dir "$input_dir" -t $slurm_timeout -n "$name" -b "$library" -d "Results" -o "$job_options" "$SCRIPT_DIR/solveAndCheck.sh")
if [[ $? -ne 0 ]]; then
  echo "ERROR: Slurm could not be called"
  echo "$output"
  exit 1
fi
echo "$output"
echo "Send to slurm"
