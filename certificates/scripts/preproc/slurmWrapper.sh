#!/bin/bash
trap "cd \"${PWD}\"" EXIT

#------------------------------------------------------------------------------------
#-------------------------------------Read Input-------------------------------------
#------------------------------------------------------------------------------------

#Default values for options
timeout=350
partition=amd
wait_active=""

Help()
{
   # Display Help
   echo "Run a script on a benchmark set"
   echo "Usage: $0 <input directory ABSOLUTE path> <script name (needs to be in preproc dir)>"
   echo "Available scripts are: findUnsup.sh,findLet.sh,findSat.sh(superseeded by catalog)"
   echo
   echo "options:"
   echo "t     Set timeout for solving and producing proof"
   echo "p     Set partition"
   echo "w     Make script wait for slurm execution (could take a long time!)"
   echo "h     Print this Help."
   echo
}

while getopts ":hp:t:w" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      p) partition=$OPTARG;;
      t) timeout=$OPTARG;;
      w) wait_active=" --wait ";;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done
shift $((OPTIND - 1))

INPUT_DIR=$1
script_name=$2

if [[ "$#" -ne 2 ]]; then
  echo "Usage: $0 [options] <input directory ABSOLUTE path> <script name (needs to be in preproc dir)>"
  exit 1
fi
if ! [[ "$INPUT_DIR" =~ ^/ ]]; then
  echo "abolute path needed! $INPUT_DIR";
  exit 1
fi


echo ""
echo "Slurm options:"
echo "Partition is: amd"
echo "timeout is: $timeout"
echo "wait is: $wait_active (if empty string then off)"
echo ""


name="${script_name%.sh}"


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
SUBMIT_JOB_HOME=/barrett/scratch/local/bin/


cd $INPUT_DIR/..

echo "Output will be written to ${PWD}"

benchmark_prefix_slurm="benchmark_set_"
benchmark_name="$name""_temp"
job_name=$name
benchmark_set_slurm=$benchmark_prefix_slurm$benchmark_name
WORKING_DIR_SLURM=output_"$benchmark_name"

echo "Clear old working directory $WORKING_DIR_SLURM"
rm -rf $WORKING_DIR_SLURM

echo "Write list of benchmarks to $benchmark_set_slurm"
find "$INPUT_DIR" -type f -name "*.smt2" > $benchmark_set_slurm 

script_to_run=$SCRIPT_DIR/$script_name

$SUBMIT_JOB_HOME/submit-job.sh -p $partition $wait_active -t $timeout -b $benchmark_name -d $WORKING_DIR_SLURM -n $job_name $script_to_run


