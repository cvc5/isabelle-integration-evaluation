#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <input directory> >"
    exit 1
fi

input_dir=$1

nr_total_smt=$(find $input_dir -type f -name "*.smt2" | wc -l)
echo "Found $nr_total_smt .smt2 files. Deleting all that have no corresponding .alethe proof" 

while read -r problem_file; do
    file_without_extension="${problem_file%.*}"
    echo "Processing $(basename $file_without_extension)"
    file_with_alethe=$file_without_extension".alethe"
    echo "$file_with_alethe"
    if ! [ -e $file_with_alethe ]
    then
      echo "Could not find corresponding .alethe file, deleting benchmark"
      rm $problem_file
    fi

done <<< $(find "$input_dir" -type f -name "*.smt2")



nr_total_smt=$(find $input_dir -type f -name "*.smt2" | wc -l)
echo "Remaining .smt2 files: $nr_total_smt" 

