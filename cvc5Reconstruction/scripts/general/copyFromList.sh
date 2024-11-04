#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <Name of folder benchmarks should be saved to> <Name of list of benchmarks> <Folder containing benchmarks, absolute path>"
    exit 1
fi

source config
output_dir=$BASE_DIR/$1
list_file=$BASE_DIR/$2
bench_folder=$3

cat $list_file
# Copy the selected files to the output directory



while read filename; do
    if [ -f "$bench_folder/$filename" ]; then
    	dirname=${filename%/*}
    	mkdir -p "$output_dir/$dirname"
        cp "$bench_folder/$filename" "$output_dir/$filename"
        echo "Copied $filename to $output_dir"
    else
        echo "Warning: File $filename not found!"
    fi
done <$list_file

echo "Selected files copied to $output_dir"

