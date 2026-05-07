#!/bin/bash

ISABELLE_HOME=/barrett/scratch/lachnitt/Binaries/Isabelle/
isabelle_cmd=$ISABELLE_HOME/bin/isabelle
AFP_HOME=/barrett/scratch/lachnitt/Binaries/afp-2026-04-04/thys/
session_name="Ordered_Resolution_Prover"
folder_name="Ordered_Resolution_Prover"
short_name="RP"

OUT_DIR=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/mirabelle/data/Apr20/$short_name/
export CVC5_PROOF_SOLVER=/barrett/scratch/lachnitt/Binaries/cvc5bin

declare -a theories=("Abstract_Substitution" "Clausal_Logic" "FO_Ordered_Resolution_Prover" "FO_Ordered_Resolution" "Ground_Resolution_Model" "Herbrand_Interpretation" "Inference_System" "Lazy_List_Chain" "Lazy_List_Liminf" "Map2" "Ordered_Ground_Resolution.thy" "Proving_Process.thy" "Standard_Redundancy.thy" "Unordered_Ground_Resolution")

for theory_name in "${theories[@]}"
do

  CURR_OUT_DIR=$OUT_DIR/$theory_name
  mkdir $CURR_OUT_DIR

  $isabelle_cmd mirabelle -d $AFP_HOME -O $CURR_OUT_DIR -A 'sledgehammer[provers=cvc5_proof, keep_probs=false, try0=true, keep_proofs=false]' -d $AFP_HOME/$folder_name -T $theory_name -v $session_name 

done
