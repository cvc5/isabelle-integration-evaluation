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
out_name="$set_kind"_"$bench_set"_"$config"_"rewrite_"$rare_mode
out_dir=output/
out_path=$out_dir/$out_name
$SCRIPT_DIR/runSetSlurmWrapperEvaluate.sh "$out_path/out/" "$out_path/result/out.json" "$config" "$bench_set"


saved_dir=saved_results_$set_kind"_rewrites_"$rare_mode/
cp $out_path/result/out.json $saved_dir/"$bench_set"_"$config".json

echo "Wrote to $saved_dir/"$bench_set"_"$config".json"
