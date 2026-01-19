#!/bin/bash


INPUT_DIR=$1
while read -r problem_file; do
	sed -i '/(get-unsat-core)/d' "$problem_file"
done <<< $(find $INPUT_DIR -type f -name "*.smt2")



