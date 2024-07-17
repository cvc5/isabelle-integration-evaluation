#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <Path to the folder containing benchmarks> <Path of the desired output folder>"
    exit 1
fi

source config

input_dir=$1
output_dir=$2
timeout_sec=1

echo "start deleting lets" 

find $input_dir -type f -name "*.smt2" | while read -r file; do
  new_name=${file#*$input_dir/} 
  dirname=${new_name%/*}

  mkdir -p "$output_dir/$dirname"
  cvc5_new_problem=$(timeout $timeout_sec $CVC5_HOME -o raw-benchmark --parse-only --dag-thres=0 "$file" 2>/dev/null)
    if [[ $? = 124 ]];
    then
      echo "lets could not be deleted from proof for file $file"
    else
    echo "$cvc5_new_problem"
      echo "$cvc5_new_problem" > "$output_dir/$new_name"
    fi
    
done

echo "Selected files copied to $output_dir"

