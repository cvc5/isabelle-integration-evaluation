#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <file_with_filenames>"
    exit 1
fi

# Check if the input file exists
if [ ! -f "$1" ]; then
    echo "Error: File $1 not found!"
    exit 1
fi

source config

# Create a directory to copy the selected files
output_dir="selected_files_$(date +"%Y%m%d_%H%M%S")"
mkdir "$output_dir"

# Read the input file and select 100 random lines
selected_files=($(shuf -n 100 "$1"))

# Copy the selected files to the output directory
for filename in "${selected_files[@]}"; do
    if [ -f "$filename" ]; then
        cp "$filename" "$output_dir"
        echo "Copied $filename to $output_dir"
    else
        echo "Warning: File $filename not found!"
    fi
done

echo "Selected files copied to $output_dir"

