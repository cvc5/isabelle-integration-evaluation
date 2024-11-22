#!/bin/bash

input_file=$2
dir=$1
echo "Input file $input_file"
echo "Dir with Alethe Files $dir"

BASE_DIR=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/
TEMP_DIR=$BASE_DIR
TMP_DIR=$BASE_DIR
raw_name="${input_file%.*}"
echo "Raw_name $raw_name"

alethe_proof_file=$dir/$raw_name".alethe"
echo "Alethe path $alethe_proof_file"

problem_file=$dir/$raw_name".smt2"
echo "Problem path $problem_file"



dir=$(pwd)

#export HOME=/barrett/scratch/lachnitt/Binaries/IsabelleSetUp/

#HOME=/barrett/scratch/lachnitt/Binaries/IsabelleSetUp/

HOME=$dir
export HOME=$dir


cp $problem_file $dir
echo "copied problem file"
cp $alethe_proof_file $dir
echo "copied Alethe file"

nr=$(cksum <<< "$raw_name" | cut -f 1 -d ' ')

echo "nr is: $nr"
$BASE_DIR/scripts/writeIsabelleTheory.sh $dir "../../"$raw_name".smt2" "../../"$raw_name".alethe" "$dir/outputIsabelleHi" "$nr"

echo "home: $HOME"

/barrett/scratch/lachnitt/Binaries/isabelle-emacs/bin/isabelle build -v -d ./Isabelle/ -c CheckFile$nr

/barrett/scratch/lachnitt/Binaries/isabelle-emacs/bin/isabelle build_log -v CheckFile$nr

rm "$raw_name.smt2"
rm "$raw_name.alethe"
