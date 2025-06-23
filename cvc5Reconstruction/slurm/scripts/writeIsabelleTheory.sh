#!/bin/bash

output_dir=$1
problem=$2
proof=$3
config=$4
nr=$5

if [ -z "$6" ]; then
  rewrite="0";
else
  rewrite=$6;
fi
rewrite="0";


if [ $config = "cvc5_with_rewrite" ]
then
 c="cvc5_proof"
else
 c="verit"
fi

mkdir -p $output_dir/"Isabelle"
mkdir -p $output_dir/"Isabelle/thys"

echo "
theory checkFile
  imports Main
begin

declare[[smt_oracle,smt_statistics_file=\"$config\"]]
declare[[smt_verbose=false,smt_trace=false,smt_debug_verit=false,smt_timeout=20.0,smt_reconstruction_step_timeout=10.0]]
declare[[smt_rec_evaluation,smt_alethe_no_assumption=true]]
declare[[rare_rec_mode=$rewrite]]
(*declare[[smt_statistics]]*)
(*declare[[verit_compress_proofs=false]]*)

check_smt (\"$c\")
\"$problem\"
\"$proof\"

end
" > $output_dir"/Isabelle/thys/checkFile.thy"

echo "
session CheckFile$nr in thys = \"Main\" +
options [quick_and_dirty]
sessions
  \"HOL-Library\"
theories
  checkFile
" > $output_dir"/Isabelle/ROOT"
