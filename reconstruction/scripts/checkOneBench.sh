#!/bin/bash
trap "cd \"${PWD}\"" EXIT

#Defaults for options
timeout=350
config="cvc5"

Help()
{
   # Display Help
   echo "Run the Isabelle smt-check tool on a proof and problem"
   echo "Usage: $0 <input problem file> <input proof file>"
   echo
   echo "options:"
   echo "t     Set timeout for solving and producing proof"
   echo "c     Set solver config (default cvc5). Note this might fail for verit proofs"
   echo
}

while getopts ":ht:o:s:c:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      t) timeout=$OPTARG;;
      o) declare_options=$OPTARG;;
      c) config=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done
shift $((OPTIND - 1))

if [[ "$#" -ne 2 ]]; then
  Help
  exit 1
fi

input_problem_file=$1
input_proof_file=$2

ISABELLE_PATH=/barrett/scratch/lachnitt/Binaries/Isabelle/bin/
export USER_HOME=/barrett/scratch/lachnitt/Binaries/IsabelleSetUp/
export ISABELLE_SMT_CVC_SPY="${PWD}/spy.txt"
ISABELLE_SMT_CVC_SPY="${PWD}/spy.txt"

declare_options_str=""
if ! [[ -z "$declare_options" ]]; then 
  declare_options_str="-o $declare_options"
fi

config_str="-s $config"

start_time=$(date +%s%N)
output=$(timeout $timeout $ISABELLE_PATH/isabelle smt_check $declare_options_str $config_str -i $input_problem_file -p $input_proof_file 2>&1)
return_value=$?
end_time=$(date +%s%N)

echo "$output" | sed  -E "/^(Warning|###|$)/d"
echo "return_value: $return_value"
checking_time=$((end_time - start_time))
echo "(\"CHECKING_TIME\", $checking_time)"

#$ISABELLE_PATH/isabelle build_log

