#!/bin/bash
trap "cd \"${PWD}\"" EXIT

#Defaults for options
delete=0

Help()
{
   # Display Help
   echo "Evaluate the result of running a solver on a dataset with runSolversWrapper.sh"
   echo "Usage: $0 <input dir> <output dir> <output file base name>"
   echo "proof will be stored in output dir. Log data will be stored in output_file_base_name.json and
         output_file_base_name.csv in the output dir"
   echo
   echo "options:"
   echo "d     Remove benchmark from tmp directory"
   echo "h     Print this Help."
   echo
}

while getopts ":hd" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      d) delete=1;;
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

input_dir=$1
output_dir=$2
output_file=$3

if ! [[ "$output_dir" =~ ^/ ]]; then
  output_dir=$(pwd)"/"$output_dir
fi

nr_proofs=$(find "$input_dir" -type f -name "*.alethe" | wc -l)

if [[ $nr_proofs = "0" ]]; then
  echo "No proofs found. Stopped evaluation run. Did not delete any files."
  exit -1
fi

#Remove double slashes in file path
input_dir="${input_dir//\/\//\/}"


rm -rf $output_dir

output_file_json=$output_file".json"
echo "[" > $output_file_json
output_file_csv=$output_file".csv"
rm -f $output_file_csv


while read -r output_log; do
  while IFS= read -r line; do
  case "$line" in
    *:*)
      key=${line%%:*}   # part before first colon
      value=${line#*: }  # part after first colon

      case "$key" in
        relative_benchmark_path)
  	  rel_path=$value
          ;;
        outcome)
	  outcome=$value
          ;;
        proof_name)
	  proof_name=$value
          ;; 
	problem_path)
	  problem_path=$value
          ;; 
        json)
	  json=$value
          ;;
        *)
          #echo "Unknown key: $key → $value"
          ;;
      esac
      ;;
  esac
  done < $output_log

  if [[ $outcome = "0" ]]
  then
    mkdir -p $output_dir/$rel_path
    directory=$(dirname "$output_log")
    if [[ -e "$directory/$proof_name" ]]
    then
      if [[ $delete -eq 0 ]]
      then
        cp $directory/$proof_name $output_dir/$rel_path/
      else
        mv $directory/$proof_name $output_dir/$rel_path/
      fi
      echo "$problem_path,$output_dir/$rel_path/$proof_name" >> $output_file_csv
      prefix=$output_dir/$rel_path/
      result=$(echo "$json" | jq --arg p "$prefix" '.solving[0].proof_path = $p + .solving[0].proof_path')
      echo $result"," >> $output_file_json
    else
      echo "Could not copy $directory/$proof_name"
    fi
  fi
done <<< $(find "$input_dir" -type f -name "output.log")

#Check last character
sed -i '$s/,$//' "$output_file_json"
echo "]" >> $output_file_json

mkdir -p $output_dir/old_runs
cp $output_file_json $output_dir/old_runs/"log_$(date +%Y-%m-%d_%H-%M-%S).json"
