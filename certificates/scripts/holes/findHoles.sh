#!/bin/bash

input_file=$1

if ! [[ $# -eq 1 ]]; then
    echo "Usage: $0 <input file>"
    exit 1
fi

unsupp=$(grep -c -e ":rule hole" $input_file)

out_str="res: $input_file, "
if ! [[ $unsupp = "0" ]];
then
  res_str="hole" 
else
  res_str="complete"
fi

echo $out_str$res_str








