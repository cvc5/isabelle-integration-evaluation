#!/bin/bash

directory=$1
config=$2
base_dir=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/

declare -a dir_names=("20170829-Rodin" "2018-Goel-hwbench" "20190906-CLEARSY" "eq_diamond" "NEQ" "PEQ" "QG-classification/loops6" "QG-classification/qg7" "QG-classification/qg5" "QG-classification/qg6" "SEQ" "TypeSafe")


for dir in "${dir_names[@]}"
do
  dir_name=$(basename $dir)
  new_bench_dir="$directory/$dir_name/$dir_name/"

  if [ -d "$new_bench_dir" ]
  then
    mkdir -p "$directory/result/$dir"
    ./scripts/collectOutput.sh $new_bench_dir "$directory"/result/$dir $config
  fi
  python3 ./scripts/analyzeErrors3.py "$directory/result/$dir/all_checking.json" $dir_name
    #python3 ./analyzeErrors2.py "benchmarks_QF_UF"/result/$dir
done

