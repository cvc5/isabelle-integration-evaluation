#!/bin/bash
source config

if [ $# -eq 0 ]; then
    echo "Usage: $0 <output file,benchmark_name,benchmark path,more details (false/true),append str>"
    exit 1
fi

output_file=$1
benchmark_name=$2
filepath=$3
details=$4
appendix=$5
has_appendix=${#appendix}

if [[ $has_appendix -ne 0 ]] ;
then
  appendix=', '"$appendix"' '
else
  appendix="" 
fi;

details_str=""
if $details ;
then
 logic=$(grep -oP '\(set-logic \K[^)]+(?=\))' $filepath)
 details_str=', "logic": "'$logic'" ' 
fi;


echo '{"benchmark_name" : "'$benchmark_name'", "path": "'$filepath'"' $details_str $appendix'},'>> $output_file
