#!/bin/bash

SCRIPT_DIR="/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/certificates/scripts/proofs/"
BENCH_PATH="/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/certificates/data/SMTLIB/"
cd $BENCH_PATH

declare -a logics=("LIA" "LRA" "QF_IDL" "QF_LIA" "QF_LRA" "QF_LRA" "QF_RDL" "QF_UF" "QF_UFIDL" "QF_UFLIA" "QF_UFLRA" "UF" "UFIDL" "UFLIA" "UFLRA" "QF_BV" "NIA")
declare -a configs=("verit" "cvc5")


#------------------------------------------------------------------------------------
#-------------------------------------Read Input-------------------------------------
#------------------------------------------------------------------------------------

#Default values for options
timeout=350
partition=quad

# Flag to detect if -l or -c was used
override_logics=false
override_configs=false

Help()
{
   # Display Help
   echo "Runs cvc5 and veriT on all SMT-LIB libraries unless option -l or -c is used"
   echo
   echo "options:"
   echo "l     Run on specific logic (e.g., QF_LRA). Can give several arguments with -l"
   echo "c     Run a specific config (verit or cvc5). Can give several arguments with -c"
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
      configs+=("$OPTARG")
      ;;

      p) partition=$OPTARG;;
      t) timeout=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

for l in "${logics[@]}"
do
   echo "$l"
   CURRENT_DIR="${BENCH_PATH}$l/"
   CURRENT_PROBLEM_DIR="${CURRENT_DIR}$l/"
   cd $CURRENT_DIR
   for c in "${configs[@]}"
   do
	   output=$(${SCRIPT_DIR}/runSolversWrapper.sh -p $partition -t $timeout $CURRENT_PROBLEM_DIR proofs/"$c"_alethe_tmp $l $c)
   done
done


