#!/bin/bash

SCRIPT_DIR="/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/reconstruction/scripts/"
BENCH_PATH="/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/certificates/data/SMTLIB/"
REC_PATH="/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/reconstruction/data/SMTLIB/"
cd $REC_PATH

declare -a logics=("LIA" "LRA" "QF_IDL" "QF_LIA" "QF_LRA" "QF_LRA" "QF_RDL" "QF_UF" "QF_UFIDL" "QF_UFLIA" "QF_UFLRA" "UF" "UFIDL" "UFLIA" "UFLRA")

declare -a configs=("verit" "cvc5")

#------------------------------------------------------------------------------------
#-------------------------------------Read Input-------------------------------------
#------------------------------------------------------------------------------------

#Default values for options
timeout=350
partition=quad

# Flag to detect if -l or -c was used
override_logics=false
config="N/A"

Help()
{
   # Display Help
   echo "Runs Isabelle on all proofs  unless option -l  is used"
   echo
   echo "options:"
   echo "l     Run on specific logic (e.g., QF_LRA). Can give several arguments with -l"
   echo "c     Set the config (verit or cvc5)"
   echo "t     Set timeout for slurm (each separate call to slurm has to use this timeout not this script itself)"
   echo "p     Override partition for calls to slurm"
   echo "h     Print this Help."
   echo
}

while getopts ":hp:t:l:c:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      l)
      if [ -z "$OPTARG" ]; then
        echo "Error: -l requires a non-empty argument"
        exit 1
      fi
      # On first -l, clear default array
      if [ "$override_logics" = false ]; then
        logics=()
        override_logics=true
      fi
      logics+=("$OPTARG")
      ;;
      c)
      # On first -c, clear default array
      if [ "$override_configs" = false ]; then
        configs=()
        override_configs=true
      fi
      if [ -z "$OPTARG" ]; then
        echo "Error: -c requires a non-empty argument"
        exit 1
      fi
      configs+=("$OPTARG")
      ;;
      p)
      if [ -z "$OPTARG" ]; then
        echo "Error: -p requires a non-empty argument"
        exit 1
      fi
      partition=$OPTARG;;
      t)
      if [ -z "$OPTARG" ]; then
        echo "Error: -t requires a non-empty argument"
        exit 1
      fi
      timeout=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

for l in "${logics[@]}"
do
   echo "$l"
   CURRENT_DIR="${REC_PATH}$l/"
   cd $CURRENT_DIR
   CURRENT_BENCH_DIR="${BENCH_PATH}$l/"
   CURRENT_BENCH_PROBLEM_DIR="${BENCH_PATH}$l/$l/"
   for c in "${configs[@]}"
   do
     CURRENT_BENCH_CSV_FILE="${BENCH_PATH}$l/proofs/${c}_alethe.csv"
     CURRENT_BENCH_PROOF_DIR="${BENCH_PATH}$l/proofs/${c}_alethe/"
     RUN_OUTPUT_DIR=${c}_alethe_tmp
     mkdir -p $RUN_OUTPUT_DIR
     output=$(${SCRIPT_DIR}/checkSlurmWrapper.sh -p $partition -t $timeout $CURRENT_BENCH_CSV_FILE $CURRENT_BENCH_PROOF_DIR $CURRENT_BENCH_PROBLEM_DIR $RUN_OUTPUT_DIR $l $c)
     echo $output
   done
done


