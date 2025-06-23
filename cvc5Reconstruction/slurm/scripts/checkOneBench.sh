#!/bin/bash

config=$1
base_dir=$2
input_file=$3

rare_mode=0


  echo "input_file: $input_file"
  echo "config: $config"
  echo "base_dir: $base_dir"
if [[ "$input_file" = ".smt2/" ]]
then
 echo "ERROR: smt2 file instead of alethe file given"
 exit -1
else
  SLURM_DIR=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/
  raw_name="${input_file%.*}"
  raw_filename="$(basename $raw_name)"
  echo $raw_name
  proof_file=$base_dir/$raw_name".alethe"
  problem_file=$base_dir/$raw_name".smt2"
  echo "proof_file: $proof_file"
  echo "problem_path: $problem_file"
  echo "bench_name: $raw_filename"

  cp $problem_file .
  echo "copied problem file"
  cp $proof_file .
  echo "copied Alethe file"

  echo "current dir? ${PWD}"
  dir=${PWD}
  nr=$(cksum <<< $raw_name$config | cut -f 1 -d ' ')
  echo $nr
  proof_file_is="../../"$raw_filename".alethe"
  problem_file_is="../../"$raw_filename".smt2"
  $SLURM_DIR/scripts/writeIsabelleTheory.sh $dir $problem_file_is $proof_file_is  $config $nr $rare_mode

  echo "Finished writing theory, now run"
  /barrett/scratch/lachnitt/Binaries/isabelle-emacs/bin/isabelle build -v -d ./Isabelle/ -c CheckFile$nr
   echo "Finished, now output log"
  /barrett/scratch/lachnitt/Binaries/isabelle-emacs/bin/isabelle build_log -v CheckFile$nr

fi
