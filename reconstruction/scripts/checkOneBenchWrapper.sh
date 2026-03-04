#!/bin/bash
trap "cd \"${PWD}\"" EXIT

#Defaults for options
timeout=350
config="N/A"
library="N/A"

Help()
{
   # Display Help
   echo "Run the Isabelle smt-check tool on a proof and problem"
   echo "Usage: $0 <input problem dir> <input proof dir> <input prooffile>"
   echo
   echo "options:"
   echo "t     Set timeout for solving and producing proof"
   echo "c     Set config"
   echo "l     Set library"
   echo
}

while getopts ":ht:c:l:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      t) timeout=$OPTARG;;
      c) config=$OPTARG;;
      l) library=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done
shift $((OPTIND - 1))

if [[ "$#" -ne 3 ]]; then
  Help
  exit 1
fi

input_problem_dir=$1
input_proof_dir=$2
input_file=$3

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
# "${input_problem_dir} ${input_proof_dir} ${config} ${lib_name} $timeout"

relative_proof_path="${input_file#$input_proof_dir}"
relative_path="${relative_proof_path%.alethe}"
relative_problem_path="$relative_path".smt2
problem_path=$input_problem_dir/$relative_problem_path


$SCRIPT_DIR/checkOneBench.sh $problem_path $input_file 
