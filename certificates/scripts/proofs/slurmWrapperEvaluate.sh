#!/bin/bash

input_dir=$1
output_dir=$2
output_file=$2

if ! [[ $# -eq 3 ]]; then
    echo "Usage: $0 <input dir> <output dir> <output file>"
    exit 1
fi

rm -rf $output_dir
rm -f $output_file

while read -r output_log; do
  rel_path=$(cat $output_log | grep "relative_benchmark_path:" | sed 's/.*relative_benchmark_path: //')
  proof_name=$(cat $output_log | grep "proof_name:" | sed 's/.*proof_name: //')
  mkdir -p $output_dir/$rel_path
  directory=$(dirname "$output_log")
  cp $directory/$proof_name $output_dir/$rel_path/
done <<< $(find "$input_dir" -type f -name "output.log")




