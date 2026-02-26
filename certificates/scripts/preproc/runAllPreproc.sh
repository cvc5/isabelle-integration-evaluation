#!/bin/bash
trap "cd \"${PWD}\"" EXIT


#------------------------------------------------------------------------------------
#-------------------------------------Read Input-------------------------------------
#------------------------------------------------------------------------------------

if ! [ $# -ge 2 ]; then
  echo "Usage: $0 <input_dir (ABSOLUTE PATH)> <output_dir>"
  echo "Run with -h for available options"
  exit 1
fi

#Default values
timeout=350
partition=quad

Help()
{
   # Display Help
   echo "<description>"
   echo
   echo "options:"
   echo "t     Set timeout for slurm (each separate call to slurm has to use this timeout not this script itself)"
   echo "p     Override partition for calls to slurm"
   echo "h     Print this Help."
   echo
}

while getopts ":hp:t:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      p) partition=$OPTARG;;
      t) timeout=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

#Read positional arguments
shift $((OPTIND - 1))
INPUT_DIR=$1
OUTPUT_DIR=$2

if ! [[ "$INPUT_DIR" =~ ^/ ]]; then
  echo "absolute path needed! $INPUT_DIR";
  exit 1
fi



#------------------------------------------------------------------------------------
#-----------------------------------Functionality------------------------------------
#------------------------------------------------------------------------------------

read -p "Have you deleted SAT or UNKNOWN benchmark from the catalog yet? If you want to proceed press enter otherwise ctrl+c" check

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd $OUTPUT_DIR
mkdir -p preproc_logs

nr_bench=$(find . -type f -name "*.smt2" | wc -l)
echo "Found $nr_bench benchmarks"

echo "------------------------------"

echo "Renaming any .smt_in files to .smt2"
$SCRIPT_DIR/renameExtension.sh $INPUT_DIR

echo "Removing any ~ in problem"
$SCRIPT_DIR/removeTilde.sh $INPUT_DIR

echo "Deleting (get-unsat-core) commands"
$SCRIPT_DIR/removeGetUnsatCore.sh $INPUT_DIR

echo "------------------------------"


echo "Rename identifiers in bars"
$SCRIPT_DIR/renameIdentifierBars.py $INPUT_DIR

echo "Find unsupported benchmarks"
output=$($SCRIPT_DIR/slurmWrapper.sh -w -p $partition -t $timeout $INPUT_DIR findUnsup.sh)
echo $output >> preproc_logs/log.out

echo "Evaluate unsupported benchmarks"
$SCRIPT_DIR/slurmWrapperEvaluate.sh output_findUnsup_temp preproc_logs/unsup.csv
rm -rf benchmark_set_findUnsup_temp output_findUnsup_temp
$SCRIPT_DIR/deleteFromCsv.sh preproc_logs/unsup.csv


echo "Delete Lets from problem"
output=$($SCRIPT_DIR/slurmWrapper.sh -w -p $partition -t $timeout $INPUT_DIR findLet.sh)
echo $output >> preproc_logs/log.out

echo "Copy benchmark without lets and delete those where lets could not be deleted"
$SCRIPT_DIR/slurmWrapperEvaluate.sh output_findLet_temp "preproc_logs/let.csv"
$SCRIPT_DIR/deleteLetFromCsv.sh "preproc_logs/let.csv" $INPUT_DIR

rm -rf benchmark_set_findLet_temp output_findLet_temp

