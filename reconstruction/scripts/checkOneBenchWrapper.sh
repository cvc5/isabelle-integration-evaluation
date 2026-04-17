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
   echo "o     Set declare options"
   echo
}

while getopts ":ht:c:l:o:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      t) timeout=$OPTARG;;
      c) config=$OPTARG;;
      l) library=$OPTARG;;
      o) declare_options=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done
shift $((OPTIND - 1))

input_problem_dir=$1
input_proof_dir=$2
input_file=$3

#if [[ "$#" -ne 3 ]]; then
#  Help
#  echo $#
#  exit 1
#fi

#SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
SCRIPT_DIR=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/reconstruction/scripts/

relative_proof_path="${input_file#$input_proof_dir}"
relative_path="${relative_proof_path%.alethe}"
relative_problem_path="$relative_path".smt2
problem_path=$input_problem_dir/$relative_problem_path

echo "(\"PROOF_FILE\",\"$input_file\")"
echo "(\"PROBLEM_FILE\",\"$problem_path\")"


declare_options_str=""
if ! [[ -z "$declare_options" ]]; then
  declare_options_str="-o $declare_options"
fi

$SCRIPT_DIR/checkOneBench.sh -t $timeout $declare_options_str $problem_path $input_file 
