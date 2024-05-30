#!/bin/bash

source config



# Main

solver=$1
echo "solver $solver"
stats_dir=$2
echo "stats_dir $stats_dir"

output_dir="$ERROR_HOME"
echo "Copy errors"

while IFS="" read -r filename || [ -n "$filename" ]
do
 input_file="$Result_BENCHMARK_HOME/${filename}"
 cp $input_file $output_dir
 proof_file="$Result_BENCHMARK_HOME/${filename%.*}.alethe"
 cp $proof_file $output_dir

 
 basefilename=$(basename "${filename%.*}")
 new_problem_name="$stats_dir"_"$solver"_"$basefilename"
 mv "$output_dir$basefilename.smt2" "$output_dir$new_problem_name.smt2"
 mv "$output_dir$basefilename.alethe" "$output_dir$new_problem_name.alethe"
done <"$ERROR_LOG"

echo "" > "$ERROR_LOG"
