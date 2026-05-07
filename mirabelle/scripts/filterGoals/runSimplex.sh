#!/bin/bash

ISABELLE_HOME=/barrett/scratch/lachnitt/Binaries/Isabelle/
isabelle_cmd=$ISABELLE_HOME/bin/isabelle
AFP_HOME=/barrett/scratch/lachnitt/Binaries/afp-2026-04-04/thys/
session_name="Simplex"
folder_name="Simplex"
short_name="Simplex"

OUT_DIR=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/mirabelle/data/Apr20/$short_name/
export CVC5_PROOF_SOLVER=/barrett/scratch/lachnitt/Binaries/cvc5bin
export ISABELLE_VERIT=/barrett/scratch/lachnitt/Binaries/verit/veriT

declare -a theories=("Abstract_Linear_Poly" "Linear_Poly_Maps" "Rel_Chain" "Simplex_Algebra" "Simplex_Incremental" "QDelta" "Simplex_Auxiliary" "Simplex")

for theory_name in "${theories[@]}"
do

  CURR_OUT_DIR=$OUT_DIR/$theory_name
  mkdir $CURR_OUT_DIR

  $isabelle_cmd mirabelle -d $AFP_HOME -O $CURR_OUT_DIR -A 'sledgehammer[fact_filter=mepo,  provers=cvc5_proof, keep_probs=false, try0=true, keep_proofs=false]' -d $AFP_HOME/$folder_name -T $theory_name -v $session_name 

done
