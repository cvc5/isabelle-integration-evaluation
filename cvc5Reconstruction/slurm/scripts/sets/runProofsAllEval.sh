#!/bin/bash

if ! [ $# -eq 2 ]; then
    echo "Usage: $0 <bench_set> <set_kind>"
    exit 1
fi

bench_set=$1
set_kind=$2

SCRIPT_DIR=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/scripts/
cd /barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/


configs=( "cvc5_with_rewrite" "verit")

for config in "${configs[@]}"
do
  $SCRIPT_DIR/sets/runProofsEval.sh $config $bench_set $set_kind
done

saved_dir=saved_results_$set_kind/
/barrett/scratch/lachnitt/Binaries/my-venv/bin/python3 $SCRIPT_DIR/combineCheckerOutput.py $saved_dir/"$bench_set"_cvc5_with_rewrite.json $saved_dir/"$bench_set"_verit.json $saved_dir/"$bench_set"_all.json




