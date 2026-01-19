#!/bin/bash

input_dir=$1
output_file=$2

if ! [[ $# -eq 2 ]]; then
    echo "Usage: $0 <input dir> <output file>"
    exit 1
fi

rm -f $output_file

while read -r problem_file; do
  entry=$(cat $problem_file | grep "res:" | sed 's/.*res: //')
  echo "$entry, " >> $output_file
done <<< $(find "$input_dir" -type f -name "output.log")


total=$(cat $output_file | wc -l)
echo "Total: $total "
awk -F',' '{count[$2]++} END {for (v in count) print v, count[v]}' $output_file


