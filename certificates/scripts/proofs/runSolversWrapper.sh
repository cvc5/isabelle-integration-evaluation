#!/bin/bash
trap "cd \"${PWD}\"" EXIT

input_dir=$1
output_dir=$2
lib_name=$3
config=$4

if ! [ $# -ge 4 ]; then
  echo "Usage: $0 <input_dir ABSOLUTE PATH> <output_dir> <library_name> <config>"
  exit 1
fi

timeout=350
partition=octa

Help()
{
   # Display Help
   echo "Run a solver (cvc5_with_rewrite, cvc5_without_rewrite or verit) on a benchmark set"
   echo
   echo "options:"
   echo "t     Set timeout for solving and producing proof"
   echo "p     Override partition in config"
   echo "h     Print this Help."
   echo
}

while getopts ":hp:t:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      p) partition=$OPTARG;;
      t) timeout=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

#set slurm timout
slurm_timeout=$((timeout + 100))
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"


rm -rf $output_dir/*
mkdir -p "$output_dir"
cd "$output_dir"
mkdir -p "Results/"

for current_dir_path in $input_dir/*/ ; do
  echo $current_dir_path  
  dir_name=$(basename "$current_dir_path")
  echo $dir_name 
  bench_file="benchmark_set_$dir_name"
  touch $bench_file
  echo "Created $bench_file"
  nr_benchs=$(find $current_dir_path -type f -name "*.smt2" | wc -l)
  find $current_dir_path -type f -name "*.smt2" > $bench_file
  
  TEMP_OUT="Results/$dir_name"
  name="runSolver_""$config""_""$lib_name""_""$dir_name"
  if [[ $nr_benchs -ne 0 ]]
  then
    /barrett/scratch/local/bin/submit-job.sh --partition "$partition" --full-access-dir $current_dir_path -t $slurm_timeout -n "$name" -b "$dir_name" -d $TEMP_OUT -o "$config $lib_name $input_dir" $SCRIPT_DIR/runSolvers.sh
  fi
done

cd ..
