#!/bin/bash

if ! [ $# -eq 4 ]; then
    echo "Usage: $0 <config> <bench_set> <set_kind> <rare_mode>"
    exit 1
fi

config=$1
bench_set=$2
set_kind=$3
rare_mode=$4

SCRIPT_DIR=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/scripts/


cd /barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/
out_name="$set_kind"_"$bench_set"_"$config""_rewrite_"$rare_mode
out_dir=output/$out_name
echo "Output will be written to: $out_dir"

rm -rf $out_dir
base_bench_path=/barrett/scratch/lachnitt/non-incremental/"$set_kind"_sets/"$bench_set"_"$set_kind"/rewrites/
$SCRIPT_DIR/runSet.sh "$base_bench_path/list_viable_rewrites_sample.txt" "$base_bench_path/rewrites_selection/" "$config" "$out_name"

