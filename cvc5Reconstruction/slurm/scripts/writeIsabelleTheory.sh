#!/bin/bash

output_dir=$1
problem=$2
proof=$3
output_file=$4
nr=$5

mkdir -p $output_dir/"Isabelle"
mkdir -p $output_dir/"Isabelle/thys"

echo "
theory checkFile
  imports \"HOL-CVC.SMT_CVC\" \"HOL.Real\"
begin

declare[[smt_oracle,smt_statistics_file=\"outputIsabelle$nr\"]]
declare[[smt_verbose=false,smt_trace=false,smt_debug_verit=false,smt_timeout=10.0,smt_reconstruction_step_timeout=5.0]]
declare[[smt_rec_evaluation,smt_alethe_no_assumption=true]]

check_smt (\"cvc5_proof\")
\"$problem\"
\"$proof\"

end
" > $output_dir"/Isabelle/thys/checkFile.thy"

echo "
session CheckFile$nr in thys = \"HOL-CVC\" +
options [quick_and_dirty]
sessions
  \"HOL-Library\"
theories
  checkFile
" > $output_dir"/Isabelle/ROOT"
