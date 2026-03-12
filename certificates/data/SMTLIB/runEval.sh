#!/bin/bash

SCRIPT_DIR="/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/certificates/scripts/proofs/"
SCRIPT_ANALYZE_DIR="/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/certificates/scripts/analyze/"
BENCH_PATH="/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/certificates/data/SMTLIB/"
cd $BENCH_PATH

declare -a logics=("LIA" "LRA" "QF_IDL" "QF_LIA" "QF_LRA" "QF_RDL" "QF_UF" "QF_UFIDL" "QF_UFLIA" "QF_UFLRA" "UF" "UFIDL" "UFLIA" "UFLRA")
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
no_evaluate=false

Help()
{
   # Display Help
   echo "Runs cvc5 and veriT on all SMT-LIB libraries unless option -l or -c is used"
   echo
   echo "options:"
   echo "l     Run on specific logic (e.g., QF_LRA). Can give several arguments with -l"
   echo "c     Run a specific config (verit or cvc5_with_rewrite). Can give several arguments with -c"
   echo "a     Only run analyze script don't update .json files or copy proofs"
   echo "h     Print this Help."
   echo
}

# Convert long options to short equivalents
args=()
for arg in "$@"; do
  case "$arg" in
    --help)    args+=(-h) ;;
    --logic)   args+=(-l) ;;
    --config)  args+=(-c) ;;
    --analyze) args+=(-a) ;;
    *)         args+=("$arg") ;;
  esac
done
set -- "${args[@]}"

while getopts ":hl:c:a" option; do
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
     a)
       no_evaluate=true
      ;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

mkdir -p ${BENCH_PATH}/logs
log_file=${BENCH_PATH}/logs/"$(date +%Y-%m-%d_%H-%M-%S).json"
rm -rf ${BENCH_PATH}/all.json

for l in "${logics[@]}"
do
   echo "$l"
   CURRENT_DIR="${BENCH_PATH}$l/proofs"

   rm -rf "${CURRENT_DIR}/all.json"

   for c in "${configs[@]}"
   do
     CURRENT_PROOF_DIR="${CURRENT_DIR}/${c}_alethe_tmp/"
     cd $CURRENT_DIR
     if [ "$no_evaluate" = false ]; then
       ${SCRIPT_DIR}/slurmWrapperEvaluate.sh $CURRENT_PROOF_DIR ${c}_alethe ${c}_alethe
     fi
     python3 ${SCRIPT_DIR}/mergeJson.py "${CURRENT_DIR}/${c}_alethe.json" "${CURRENT_DIR}/all.json" "${CURRENT_DIR}/all.json"
   done
   python3 ${SCRIPT_DIR}/mergeJson.py "${CURRENT_DIR}/${c}_alethe.json" "${CURRENT_DIR}/all.json" "${CURRENT_DIR}/all.json"
   python3 ${SCRIPT_DIR}/mergeJson.py "${CURRENT_DIR}/all.json" ${BENCH_PATH}/all.json ${BENCH_PATH}/all.json
done

cat ${BENCH_PATH}/all.json > $log_file
