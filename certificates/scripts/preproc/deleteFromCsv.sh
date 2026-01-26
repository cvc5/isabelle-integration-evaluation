#!/bin/bash
trap "cd \"${PWD}\"" EXIT


input_file=$1

SCRIPT_DIR=/barrett/scratch/lachnitt/non-incremental/scripts/
if ! [[ $# -eq 1 ]]; then
  echo "Usage: $0 <input csv file>"
  echo "Excepts a csv list with entries: path, status"
  echo "If status is unsupported or sat, delete the benchmark"
  exit 1
fi


while IFS=, read -r field1 field2
do
  if [[ $field2 == " unsupported, " ]];
  then
    rm $field1;
  fi
  if [[ $field2 == " sat, " ]];
  then
    rm $field1;
  fi
done < $input_file

