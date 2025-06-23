#!/bin/bash

if ! [ $# -eq 3 ]; then
    echo "Usage: $0 <config> <bench_set> <set_kind>"
    exit 1
fi

config=$1
bench_set=$2
set_kind=$3

SCRIPT_DIR=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/scripts/


cd /barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/
out_name="$set_kind"_"$bench_set"_"$config"
out_dir=output/$out_name
echo "Output will be written to: $out_dir"

rm -rf $out_dir
base_bench_path=/barrett/scratch/lachnitt/non-incremental/"$set_kind"_sets/"$bench_set"_"$set_kind"/proofs/
$SCRIPT_DIR/runSet.sh "$base_bench_path/list_viable_"$config".txt" "$base_bench_path/"$config"/" "$config" "$out_name"

