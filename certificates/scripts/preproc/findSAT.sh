#!/bin/bash

input_file=$1

if ! [[ $# -eq 1 ]]; then
    echo "Usage: $0 <input directory ABSOLUTE path>"
    exit 1
fi

timeout_sec=1080s
CVC5_HOME=/barrett/scratch/lachnitt/Binaries/cvc5bin

trivial=$(grep -c "(set-info :status sat)" $input_file)

if [[ $trivial -eq "0" ]]
then
  output=$(timeout $timeout_sec $CVC5_HOME  "$input_file" 2>&1)
  return_value=$?
  if [[ $return_value -ne "0" ]]
  then
    output="unsupported"
  fi
else
  output="sat"
fi

 
echo "res: $input_file, $output"
