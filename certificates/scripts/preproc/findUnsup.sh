#!/bin/bash

input_file=$1

if ! [[ $# -eq 1 ]]; then
    echo "Usage: $0 <input file>"
    exit 1
fi

unsupp=$(grep -c -e "^(define-fun" -e "^(declare-datatype" -e "^(declare-datatypes" -e "^(define-fun-rec" -e "^(define-fun-recs" -e "^(define-sort" -e "^(get-model" -e "^(pop" -e "^(push" -e "^(reset" -e "^(reset-assertions" -e "^(declare-fun |" -e "^(assert.*|" -e "^(declare-.*|" $input_file)

out_str="res: $input_file, "
if ! [[ $unsupp = "0" ]];
then
  res_str="unsupported" 
else
  res_str="supported"
fi

echo $out_str$res_str








