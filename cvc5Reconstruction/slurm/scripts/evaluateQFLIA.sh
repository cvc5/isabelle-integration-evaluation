#!/bin/bash

directory=$1
config=$2
base_dir=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/


declare -a dir_names=("20180326-Bromberger" "20210219-Dartagnan" "20220307-SMPT" "20230321-UltimateAutomizerSvcomp2023" "20231117-c_inference" "arctic-matrix" "Averest" "bofill-scheduling" "calypto" "CAV_2009_benchmarks" "check" "CIRC" "convert" "cut_lemmas" "dillig" "fft" "mathsat" "miplib2003" "pb2010" "pidgeons" "prime-cone" "rings" "rings_preprocessed" "slacks" "tightrhombus" "tropical-matrix" "wisa")

for dir in "${dir_names[@]}"
do
  #echo $dir
  dir_name=$(basename $dir)
  new_bench_dir="$directory/out/$dir_name/$dir_name/"

  if [ -d "$new_bench_dir" ]
  then
    mkdir -p "$directory/result/$dir"
    ./collectOutput.sh $new_bench_dir "$directory"/result/$dir $config
  fi
  python3 ./analyzeErrors3.py "$directory/result/$dir/all_checking.json" $dir_name
    #python3 ./analyzeErrors2.py "benchmarks_QF_UF"/result/$dir
done

