#!/bin/bash
trap "cd \"${PWD}\"" EXIT


if ! [ $# -ge 4 ]; then
  echo "Usage: $0 <input_dir ABSOLUTE PATH> <output_dir> <library_name> <config>"
  exit 1
fi

timeout=350
prev_solved=0

Help()
{
   # Display Help
   echo "Run a solver (cpc, cvc5, cvc5_without_rewrite or verit) on a benchmark set without using slurm"
   echo
   echo "options:"
   echo "t     Set timeout for solving and producing proof"
   echo "i     Only run on files in <input_file.txt>"
   echo "h     Print this Help."
   echo
}

while getopts ":ht:i:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      t) timeout=$OPTARG;;
      i) prev_solved_file=$OPTARG
         prev_solved=1;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done


#Read positional arguments
shift $((OPTIND - 1))

input_dir=$1
output_dir=$2
lib_name=$3
config=$4

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

#Delete double slashes from file paths
input_dir="${input_dir//\/\//\/}"
output_dir="${output_dir//\/\//\/}"

rm -rf $output_dir/*
mkdir -p "$output_dir"
cd "$output_dir"
mkdir -p "Results/"

for current_dir_path in $input_dir/*/ ; do
  current_dir_path="${current_dir_path//\/\//\/}"
  echo "Processing: $current_dir_path"
  dir_name=$(basename "$current_dir_path")
  bench_file=$current_dir_path/"benchmark_set_$dir_name"
  nr_benchs=$(find $current_dir_path -type f -name "*.smt2" | wc -l)
  if [[ $nr_benchs -ne 0 ]]
  then
    echo "  Found benchmarks in $dir_name"
    touch $bench_file
    if [[ $prev_solved -ne 0 ]]
    then
      find $current_dir_path -type f -name "*.smt2" > $bench_file"_tmp"
      grep -Ff $prev_solved_file $bench_file"_tmp" > $bench_file
      #rm $bench_file"_tmp"
    else
      find $current_dir_path -type f -name "*.smt2" > $bench_file
    fi 
    echo "  Created $bench_file"
    TEMP_OUT="$output_dir/Results/$dir_name"
    mkdir -p $TEMP_OUT
    TEMP_OUT="$output_dir/Results/$dir_name/$dir_name/"
    mkdir -p $TEMP_OUT
    cd $TEMP_OUT

    while IFS= read -r file
    do
      filename=$(basename $file)
      mkdir $filename
      cd $filename
      output=$($SCRIPT_DIR/runSolvers.sh ${config} ${lib_name} ${input_dir} $timeout $file)
      echo "$output" >> output.log
      cd ..
    done < $bench_file
    if [[ $? -ne 0 ]]
    then
      echo "ERROR: Solvers could not be called on benchmarks in $dir_name"
      exit -1
    fi
  else
    echo "  No benchmarks found in $dir_name. Skip this folder."	
  fi
done

cd ..
