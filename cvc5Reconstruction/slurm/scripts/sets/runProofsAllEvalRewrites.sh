#!/bin/bash

if ! [ $# -eq 3 ]; then
    echo "Usage: $0 <bench_set> <set_kind> <rare_mode>"
    exit 1
fi

bench_set=$1
set_kind=$2
rare_mode=$3

echo "Make sure Rare mode in runSet.sh is set to the proper entry!"

SCRIPT_DIR=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/scripts/
cd /barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/


configs=( "cvc5_with_rewrite")

for config in "${configs[@]}"
do
  $SCRIPT_DIR/sets/runProofsEvalRewrites.sh $config $bench_set $set_kind $rare_mode
done





