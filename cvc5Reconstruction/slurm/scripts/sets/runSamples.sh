#!/bin/bash

SCRIPT_HOME=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm


bsets=("QF_UF" "QF_LIA" "QF_LRA" "UF")

for bset in "${bsets[@]}"
do
  $SCRIPT_HOME/scripts/sets/runProofs.sh cvc5_with_rewrite "$bset" sample
done






