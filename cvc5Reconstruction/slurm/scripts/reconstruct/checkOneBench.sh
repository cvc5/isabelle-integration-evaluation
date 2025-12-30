#!/bin/bash
source /barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/scripts/config

config=$1
base_dir=$2
input_file=$3

if [[ "$input_file" = ".smt2/" ]]
then
 echo "ERROR: smt2 file instead of alethe file given"
 exit -1
elif [[ $# -ne 3 ]]
then
  echo "Usage <config> <base_dir> <input_file> (optional: rare_mode)"
 exit -1
else
  if [[ $# -eq 4 ]]
  then
    rare_mode=$4
  else
    rare_mode=0 #0 is lemma only (fail if not found), #1 is lemma and if not found simp, #2 is simp directly
  fi  

  raw_name="${input_file%.*}"
  raw_filename="$(basename $raw_name)"
  proof_file=$base_dir/$raw_name".alethe"
  problem_file=$base_dir/$raw_name".smt2"
  echo "!\"benchmark_name\": \"$raw_filename\""
  echo "!\"problem_path\": \"$problem_file\""
  echo "!\"proof_path\": \"$proof_file\""
  echo "!\"rare_mode\": $rare_mode"
  echo "INPUT_FILE: $input_file"
  echo "CONFIG: $config"
  echo "BASE_DIR: $base_dir"

  cp $problem_file .
  cp $proof_file .

  dir=${PWD}
  nr=$(cksum <<< $raw_name$config | cut -f 1 -d ' ')
  echo $nr
  proof_file_is="../../"$raw_filename".alethe"
  problem_file_is="../../"$raw_filename".smt2"

  $ISABELLE_PATH smt_check -i $raw_filename.smt2 -p $raw_filename.alethe -o $config
  #$ISABELLE_PATH components #To see paths
  
  rm $raw_filename".alethe"
  rm $raw_filename".smt2"
  

fi
