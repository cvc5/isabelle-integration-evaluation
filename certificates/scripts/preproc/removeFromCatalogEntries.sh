#!/bin/bash
trap "cd \"${PWD}\"" EXIT


input_file=$1
base_dir=$2

if ! [[ $# -eq 2 ]]; then
  echo "Usage: $0 <input csv file> <base_dir>"
  echo "Excepts a csv list with entries: family, name"
  echo "E.g., slacks,40-32.slack.smt2"
  echo "Base dir should be absolute path to directory where the toplevel folders are the families"
  echo "If it appears in the list, delete the benchmark"
  exit 1
fi

nr_bench=$(find $base_dir -type f -name "*.smt2" | wc -l)
echo "Found $nr_bench benchmarks"
sed -i 's/\r$//' "$input_file"

while IFS=',' read -r field1 field2;
do
  rm $base_dir/"$field1"/"$field2"
done < "$input_file"

nr_bench=$(find $base_dir -type f -name "*.smt2" | wc -l)
echo "After deleting sat benchmarks there remain $nr_bench benchmarks"
