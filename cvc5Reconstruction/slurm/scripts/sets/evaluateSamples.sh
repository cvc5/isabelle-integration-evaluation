#!/bin/bash

SCRIPT_HOME=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm


bsets=("QF_UF" "QF_LIA" "QF_LRA" "UF")
rm $SCRIPT_HOME/saved_results_sample/all_cvc5_with_rewrite.json

for bset in "${bsets[@]}"
do
  $SCRIPT_HOME/scripts/sets/runProofsEval.sh cvc5_with_rewrite "$bset" sample
  cp $SCRIPT_HOME/output/sample_"$bset"_cvc5_with_rewrite/result/out.json $SCRIPT_HOME/saved_results_sample/"$bset"_cvc5_with_rewrite.json
done






