#!/bin/bash

dir_names=$1
config=$2
base_dir=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/


for dir in "${dir_names[@]}"
do
  dir_name=$(basename $dir)
  new_bench_dir="$directory/out/$dir_name/$dir_name/"

  if [ -d "$new_bench_dir" ]
  then
    mkdir -p "$directory/result/$dir"
    ./collectOutput.sh $new_bench_dir "$directory"/result/$dir $config
  fi
  python3 ./analyzeErrors3.py "$directory/result/$dir/all_checking.json" $dir_name
done

