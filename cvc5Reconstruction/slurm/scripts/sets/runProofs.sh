#!/bin/bash

source /barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/scripts/config

if ! [ $# -eq 3 ]; then
    echo "Usage: $0 <config> <bench_set> <set_kind>"
    exit 1
fi

config=$1
bench_set=$2
set_kind=$3


cd $SLURM_DIR
out_name="$set_kind"_"$bench_set"_"$config"
out_dir=output/$out_name
echo "Output will be written to: $out_dir"
echo "$RECONSTRUCT_DIR"
echo "$SLURM_DIR"

rm -rf $out_dir
base_bench_path=/barrett/scratch/lachnitt/non-incremental/"$set_kind"_sets/"$bench_set"_"$set_kind"/proofs/
$RECONSTRUCT_DIR/checkBenchSet.sh "$base_bench_path/list_viable_"$config".txt" "$base_bench_path/"$config"/" "$config" "$out_name"

