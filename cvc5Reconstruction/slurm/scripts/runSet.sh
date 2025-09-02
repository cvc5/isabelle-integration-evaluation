#!/bin/bash

if ! [ $# -eq 4 ]; then
    echo "Usage: $0 <input file> <base_path> <solver_config (cvc5_with_rewrite or cvc5_without_rewrite)> <out_name>"
    exit 1
fi

input_file=$1
base_path=$2
config=$3
out_name=$4
rare_mode="2" #0 is lemma only (fail if not found), #1 is lemma and if not found simp, #2 is simp directly

echo "input_file $input_file"
echo "config $config"
echo "rare_mode $rare_mode"

timeout=1210
base_dir=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/

bench_name="$out_name"
out_dir="$base_dir/output"
cur_out_dir="$out_dir""/$out_name/"
result_dir="$cur_out_dir/result/"
bench_file=benchmark_set_"$bench_name"

mkdir -p "$cur_out_dir"
mkdir -p "$result_dir"

ls

cd $cur_out_dir

cat $input_file > $bench_file
i=$(cat "$input_file"  | wc -l)
echo "Found $i benchmarks"

/barrett/scratch/local/bin/submit-job.sh -t $timeout -p quad -b $bench_name -d "$cur_out_dir/out/" --full-access-dir /barrett/scratch/lachnitt/Binaries/IsabelleSetUp/.isabelle/ -o "$config $base_path" $base_dir/scripts/checkOneBench.sh

