#!/bin/bash

input_dir=$1
config=$2
class="QF_LIA"
declare -a dir_names=("20180326-Bromberger" "20210219-Dartagnan" "20220307-SMPT" "20230321-UltimateAutomizerSvcomp2023" "20231117-c_inference" "arctic-matrix" "Averest" "bofill-scheduling" "calypto" "CAV_2009_benchmarks" "check" "CIRC" "convert" "cut_lemmas" "dillig" "fft" "mathsat" "miplib2003" "pb2010" "pidgeons" "prime-cone" "rings" "rings_preprocessed" "slacks" "tightrhombus" "tropical-matrix" "wisa")

base_dir=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/
echo "input_dir $input_dir"

out_dir="benchmarks_""$class""_""$config"
mkdir -p "$out_dir"
mkdir -p "$out_dir/result/"
cd ./"$out_dir"

current=$(pwd)
echo "output dir: $current"

for dir in "${dir_names[@]}"
do
  echo "Benchmark set: $dir"
  dir_name=$(basename $dir)
  new_bench_dir="benchmarks_$dir_name"
  mkdir -p $new_bench_dir
  rm -rf $new_bench_dir/*
  cp -r "$input_dir/$dir/"* $new_bench_dir 

  echo "new-bench $current/$new_bench_dir"
  find $new_bench_dir/ -type f -name "*.smt2" -printf "%f\n" > benchmark_set_"$dir_name"
  /barrett/scratch/local/bin/submit-job.sh  -b $dir_name -d out/$dir_name --full-access-dir /barrett/scratch/lachnitt/Binaries/IsabelleSetUp/.isabelle/ -o $current/$new_bench_dir ../checkOneBench.sh

done
cd ..
