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
out_dir=output/
out_path=$out_dir/$out_name
$SCRIPT_DIR/runSetSlurmWrapperEvaluate.sh "$out_path/out/" "$out_path/result/out.json" "$config" "$bench_set"


saved_dir=saved_results_$set_kind/
cp $out_path/result/out.json $saved_dir/"$bench_set"_"$config".json

echo "Wrote to $saved_dir/"$bench_set"_"$config".json"
