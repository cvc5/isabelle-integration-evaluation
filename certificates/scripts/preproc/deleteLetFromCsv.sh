#!/bin/bash

input_file=$1
output_dir=$2

SCRIPT_DIR=/barrett/scratch/lachnitt/non-incremental/scripts/
if ! [[ $# -eq 2 ]]; then
    echo "Usage: $0 <input csv file> <output directory>"
    exit 1
fi

mkdir -p $output_dir


nr_supp=0
nr_unsupp=0
nr_others=0

while IFS=, read -r field1 field2 field3
do
  if [[ $(echo $field3 | grep -c "okay") -gt 0 ]] ;
  then
    nr_supp=$((nr_supp + 1))
    cp $field2 $field1
  elif [[ $(echo $field3 | grep -c "let_error") -gt 0 ]] ;
  then
    nr_unsupp=$((nr_unsupp + 1))
    rm $field1
  elif [[ $(echo $field3 | grep -c "let_timeout") -gt 0 ]] || [[ $filed3 == "" ]] ;
  then
    nr_unsupp=$((nr_unsupp + 1))
    rm $field1
  else
    nr_others=$((nr_others + 1))
  fi
done < $input_file

total=$((nr_supp+nr_unsupp+nr_others))

