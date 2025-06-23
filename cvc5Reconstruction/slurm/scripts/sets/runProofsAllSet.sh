#!/bin/bash

SCRIPT_DIR=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/scripts/

if ! [ $# -eq 1 ]; then
    echo "Usage: $0  <set_kind>"
    exit 1
fi


set_kind=$1
bench_sets=("baseline_probs" "max_facts_16" "QF_UF" "QF_LIA" "QF_LRA" "QF_LIRA" "UF" "LIA" "LRA")


for bench_set in "${bench_sets[@]}"
do
  $SCRIPT_DIR/sets/runProofsAll.sh $bench_set $set_kind
done



