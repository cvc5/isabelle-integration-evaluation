#!/bin/bash

input_dir=$1
output_dir=$2
output_file=$3

if ! [[ $# -eq 3 ]]; then
    echo "Usage: $0 <input dir> <output dir> <output file base name>"
    exit 1
fi

if ! [[ "$output_dir" =~ ^/ ]]; then
  output_dir=$(pwd)"/"$output_dir
fi

nr_proofs=$(find "$input_dir" -type f -name "*.alethe" | wc -l)

if [[ $nr_proofs = "0" ]]; then
  echo "No proofs found. Stopped evaluation run. Did not delete any files."
  exit -1
fi

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
	  echo $json"," >> $output_file_json
          ;;
        *)
          echo "Unknown key: $key → $value"
          ;;
      esac
      ;;
  esac
  done < $output_log

  if [[ $outcome = "0" ]]
  then
    mkdir -p $output_dir/$rel_path
    directory=$(dirname "$output_log")
    cp $directory/$proof_name $output_dir/$rel_path/
    echo "$problem_path,$output_dir/$rel_path/$proof_name" >> $output_file_csv
  fi
done <<< $(find "$input_dir" -type f -name "output.log")

#Check last character
sed -i '$s/,$//' "$output_file_json"
echo "]" >> $output_file_json

