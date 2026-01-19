#!/bin/bash

INPUT_DIR=$1

# Find all files with the .smt_in.smt2 extension
find $INPUT_DIR -type f -name "*.smt_in" | while read file; do
  # Rename each file by changing its extension from .smt_in to .smt2
  mv "$file" "${file%.smt_in}.smt2"
done

