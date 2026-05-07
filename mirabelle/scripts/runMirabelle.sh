#!/bin/bash

input_session_dir=$1
input_session_name=$2

ISABELLE_PATH=/barrett/scratch/lachnitt/Binaries/Isabelle/bin/
AFP=/barrett/scratch/lachnitt/Binaries/afp-2026-04-04/thys/
CURRENT_DIR="${PWD}"
USER_HOME=$CURRENT_DIR
ISABELLE_USER_HOME=$CURRENT_DIR
ISABELLE_HEAPS_SYSTEM=$CURRENT_DIR
ISABELLE_COMPONENTS_BASE=/barrett/scratch/lachnitt/Binaries/IsabelleSetUp/
ISABELLE_VERIT=/barrett/scratch/lachnitt/Binaries/verit/veriT

mkdir .isabelle
cp -r ../../Isabelle_08-Apr-2026 .isabelle/

CVC5_PROOF_SOLVER=/barrett/scratch/lachnitt/Binaries/cvc5bin $ISABELLE_PATH/isabelle mirabelle -d $AFP -O output_mirabelle_$input_session_name -A 'sledgehammer[provers=cvc5_proof, keep_probs=true, try0=false, keep_proofs=true, debug=true]' -d $input_session_dir $input_session_name
