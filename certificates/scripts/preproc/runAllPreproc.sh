#!/bin/bash
trap "cd \"${PWD}\"" EXIT

INPUT_DIR=$1
OUTPUT_DIR=$2

if ! [ $# -eq 2 ]; then
  echo "Usage: $0 <input_dir (absolute path)> <log output_dir>"
  echo "input dir is changed in place so make copy before if you want to keep original files"
  exit 1
fi


if ! [[ "$INPUT_DIR" =~ ^/ ]]; then
  echo "abolute path needed! $INPUT_DIR";
  exit 1
fi


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd $OUTPUT_DIR
mkdir -p preproc_logs

echo "------------------------------"

echo "Renaming any .smt_in files to .smt2"
$SCRIPT_DIR/renameExtension.sh $INPUT_DIR

echo "Removing any ~ in problem"
$SCRIPT_DIR/removeTilde.sh $INPUT_DIR

echo "Deleting (get-unsat-core) commands"
$SCRIPT_DIR/removeGetUnsatCore.sh $INPUT_DIR

echo "------------------------------"

nr_bench=$(find . -type f -name "*.smt2" | wc -l)
echo "Found $nr_bench benchmarks"

echo "Find unsupported benchmarks"
output=$($SCRIPT_DIR/slurmWrapper.sh -w $INPUT_DIR findUnsup.sh)
echo $output >> preproc_logs/log.out

echo "Evaluate unsupported benchmarks"
$SCRIPT_DIR/slurmWrapperEvaluate.sh output_findUnsup_temp preproc_logs/unsup.csv
rm -rf benchmark_set_findUnsup_temp output_findUnsup_temp
$SCRIPT_DIR/deleteFromCsv.sh preproc_logs/unsup.csv

echo "Find SAT benchmarks"
output=$($SCRIPT_DIR/slurmWrapper.sh -w $INPUT_DIR findSAT.sh)
echo $output >> preproc_logs/log.out

echo "Evaluate SAT benchmarks"
$SCRIPT_DIR/slurmWrapperEvaluate.sh output_findSAT_temp preproc_logs/sat.csv
rm -rf benchmark_set_findSAT_temp output_findSAT_temp
$SCRIPT_DIR/deleteFromCsv.sh preproc_logs/sat.csv


echo "Delete Lets from problem"
output=$($SCRIPT_DIR/slurmWrapper.sh -w $INPUT_DIR findLet.sh)
echo $output >> preproc_logs/log.out

echo "Copy benchmark without lets and delete those where lets could not be deleted"
$SCRIPT_DIR/slurmWrapperEvaluate.sh output_findLet_temp "preproc_logs/let.csv"
$SCRIPT_DIR/deleteLetFromCsv.sh "preproc_logs/let.csv" $INPUT_DIR
rm -rf benchmark_set_findLet_temp output_findLet_temp

