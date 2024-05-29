#!/bin/bash

source config



usage() {
 echo "Usage: $0 [OPTIONS]"
 echo "To be used by runAll internally for now"
}

handle_options() {
while getopts "h" flag; do
 case $flag in
   h)
   usage
   exit 0
   ;;
   \?)
   usage
   exit -1
   ;;
 esac
done
}


# Main

handle_options "$@" 
output_dir="$ERROR_HOME"
 echo "saveERror.sh"
 echo $output_dir
 echo $ERROR_LOG

#TODO: Make filename dependend on solver
while IFS="" read -r filename || [ -n "$filename" ]
do
 input_file="$Result_BENCHMARK_HOME/${filename}"
 echo $input_file
 cp $input_file $output_dir
 proof_file="$Result_BENCHMARK_HOME/${filename%.*}.alethe"
 cp $proof_file $output_dir
done <"$ERROR_LOG"

echo "" > "$ERROR_LOG"
