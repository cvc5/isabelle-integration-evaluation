#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <input directory>"
    exit 1
fi

input_dir=$1


for current_dir_path in $input_dir/*/ ; do

  # find benchmarks
  current_dir=$(basename "$current_dir_path")
  echo "Current directory $current_dir"
  current_checking_file=$current_dir_path"/all_checking.json"
  echo $current_checking_file
  if [ -e $current_checking_file ]
  then
    echo "Found"
  fi
    
done 
