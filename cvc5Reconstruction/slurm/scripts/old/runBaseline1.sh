#!/bin/bash

out_name=$1

cd /barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm
mkdir saved_results/benchmarks_baseline$out_name

./scripts/runSet.sh /barrett/scratch/lachnitt/non-incremental/mod_sets/baseline_probs/all_solving.txt cvc5_with_rewrite /barrett/scratch/lachnitt/non-incremental/mod_sets/baseline_probs/SMT2/ baseline $out_name


