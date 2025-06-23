#!/bin/bash

SCRIPT_DIR=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/scripts/

if ! [ $# -eq 1 ]; then
    echo "Usage: $0  <set_kind> "
    exit 1
fi


set_kind=$1
bench_sets=("baseline_probs" "max_facts_16" "QF_UF" "QF_LIA" "QF_LRA" "QF_LIRA" "UF" "LIA" "LRA")
SCRIPT_DIR=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/scripts/

out_dir=saved_results_$set_kind/
rm -rf $out_dir/*
first=true
all_log=$out_dir/all_checking.json
i=0

for bench_set in "${bench_sets[@]}"
do
  $SCRIPT_DIR/sets/runProofsAllEval.sh $bench_set $set_kind
 log_file_target=$out_dir/"$bench_set"_all.json
 if $first ;
 then
      cp $log_file_target $all_log
     first=false
 else
   i=$((i+1))
   all_log_temp=$out_dir/temp$i.json

   python3 $SCRIPT_DIR/combineCheckerOutput.py $all_log $log_file_target $all_log_temp
   cp $all_log_temp $all_log

  fi

done



