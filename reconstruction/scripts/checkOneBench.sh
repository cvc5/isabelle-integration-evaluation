#!/bin/bash
trap "cd \"${PWD}\"" EXIT

#Defaults for options
timeout=350

Help()
{
   # Display Help
   echo "Run the Isabelle smt-check tool on a proof and problem"
   echo "Usage: $0 <input problem file> <input proof file>"
   echo
   echo "options:"
   echo "t     Set timeout for solving and producing proof"
   echo
}

while getopts ":ht:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      t) timeout=$OPTARG;;
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
ISABELLE_VERSION=Isabelle_27-Mar-2026
#ISABELLE_PATH=/barrett/scratch/lachnitt/Binaries/dist-$ISABELLE_VERSION/$ISABELLE_VERSION/bin/
ISABELLE_PATH=/barrett/scratch/lachnitt/Binaries/$ISABELLE_VERSION/bin/
export USER_HOME=/barrett/scratch/lachnitt/Binaries/IsabelleSetUp/

start_time=$(date +%s%N)
output=$(timeout $timeout $ISABELLE_PATH/isabelle smt_check -i $input_problem_file -p $input_proof_file 2>&1)
return_value=$?
end_time=$(date +%s%N)

echo "$output" | sed  -E "/^(Warning|###|$)/d"
echo "return_value: $return_value"
checking_time=$((end_time - start_time))
echo "checking_time: $checking_time"

#$ISABELLE_PATH/isabelle build_log

