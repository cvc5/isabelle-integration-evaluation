#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <file_with_filenames> <nr_of_randomely_selected_files>"
    exit 1
fi

# Check if the input file exists
if [ ! -f "$1" ]; then
    echo "Error: File $1 not found!"
    exit 1
fi

source config

input_file=$1
nr_out_files=$2

# Read the input file and select 100 random lines
selected_files=($(shuf -n $nr_out_files "$input_file"))

# Copy the selected files to the output directory
for filename in "${selected_files[@]}"; do
  echo $filename
done
