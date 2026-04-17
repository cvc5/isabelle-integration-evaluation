#!/bin/bash
trap "cd \"${PWD}\"" EXIT



timeout=350
partition="quad"

Help()
{
   # Display Help
   echo "Run Isabelle on a benchmark set"
   echo "Usage: <input .csv file> <proof dir> <problem dir> <output dir> <lib name, e.g. QF_UF> <config, e.g., cvc5>"
   echo
   echo "options:"
   echo "t     Set timeout for solving and producing proof"
   echo "p     Override partition in config"
   echo "o     Set declare options"
   echo "h     Print this Help."
   echo
}

while getopts ":hp:t:o:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      p) partition=$OPTARG;;
      t) timeout=$OPTARG;;
      o) declare_options=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done


#Read positional arguments
shift $((OPTIND - 1))

input_file=$1
input_proof_dir=$2
input_problem_dir=$3
output_dir=$4
lib_name=$5
config=$6

if ! [ $# -ge 6 ]; then
  Help
  exit 1
fi

#set slurm timout
slurm_timeout=$((timeout + 100))
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"


rm -rf $output_dir/*
mkdir -p "$output_dir"
cd "$output_dir"
mkdir -p "Results/"
id="$lib_name"_"$config"
bench_file="benchmark_set_""$id"
touch $bench_file
echo "  Created $bench_file"

while IFS=, read -r field1 field2
do
  echo "$field2" >> $bench_file
done < $input_file

declare_options_str=""
if ! [[ -z "$declare_options" ]]; then
  declare_options_str="-o $declare_options"
fi

nr_benchs=$(cat $input_file | wc -l)
if [[ $nr_benchs -ne 0 ]]
then
    TEMP_OUT="Results/cvc5test"
    name="runSolver"_"$lib_name"_"$config"
    output=$(/barrett/scratch/local/bin/submit-job.sh --partition "$partition" --full-access-dir $input_problem_dir -t $slurm_timeout -n "$name" -b "$id" -d $TEMP_OUT -o "-t $timeout ${declare_options_str} ${input_problem_dir} ${input_proof_dir}" $SCRIPT_DIR/checkOneBenchWrapper.sh)
    if [[ $? -ne 0 ]]
    then
      echo "ERROR: Slurm could not be called on benchmarks"
      echo $output
      exit -1
    else
      echo "  Send to slurm"
    fi
else
     echo "  No benchmarks found. Skip."	
fi

