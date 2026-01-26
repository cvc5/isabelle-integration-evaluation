#!/bin/bash

input_file=$1

CVC5_HOME=/barrett/scratch/lachnitt/Binaries/cvc5bin
timeout_sec=10s

if ! [[ $# -eq 1 ]]; then
    echo "Usage: $0 <input file>"
    exit 1
fi


echo -n "res: $input_file,"
  filename=$(basename $input_file)
  filename=${PWD}/$filename
  echo -n "$filename,"
  cvc5_new_problem=$(timeout $timeout_sec $CVC5_HOME -o raw-benchmark --parse-only --dag-thres=0 "$input_file" 2>/dev/null)
  ret=$?
    if [[ $ret = 1 ]]
    then
      res_str="let_error" 
    elif [[ $ret = 124 ]]
    then
      res_str="let_timeout" 
    else
      res_str="okay"
      echo "$cvc5_new_problem" > $(basename $input_file)
    fi

echo $res_str








