#!/bin/bash

source config

write_result()
{
  solver_name=$1
  solver_command=$2
  new_file_ending=$3
  file=$4

  new_file="${file##*/}"

  start_time=$(date +%s%N)
  output=$(eval "$solver_command")
  local return_value=$?
  end_time=$(date +%s%N)

  if [ $return_value = 124 ] ; 
  then 
    echo "Timeout"
    echo "$new_file, $solver_name, timeout" >> $curr_res_file
  elif [ $return_value = 1 ] ;
  then 
    echo "Solver $solver_name$ could not solve problem!"
    echo "$new_file, $solver_name, error" >> $curr_res_file
  else
    new_file="${new_file%.*}"  
    resultFile=$Result_BENCHMARK_HOME$new_file$new_file_ending;
    touch $resultFile
    echo "$output">$resultFile;

    #TODO: Copy problem
    elapsed_time=$((end_time - start_time))
    echo "$new_file, $solver_name, $elapsed_time" >> $curr_res_file
  fi
 
 }

call_cvc5_rewrite()
{
  file=$1
  local cvc5="$CVC5_HOME --proof-format-mode=alethe --dump-proofs --produce-proofs --proof-granularity=dsl-rewrite --full-saturate-quant --no-stats --sat-random-seed=1 --lang=smt2 $file"
  write_result "cvc5_with_rewrite" "$cvc5" "_rewrite.alethe" $file;

}

call_cvc5_without_rewrite()
{
  file=$1
  local cvc5="$CVC5_HOME --proof-format-mode=alethe --dump-proofs --produce-proofs --full-saturate-quant --no-stats --sat-random-seed=1 --lang=smt2 $file"
  write_result "cvc5_without_rewrite" "$cvc5" "without_rewrite.alethe" $file;

}



#Make result directory
current_time=$(date "+%Y.%m.%d-%H.%M.%S")
curr_res_file=$EVAL_RES$current_time".txt"
#curr_res_dir=$EVAL_RES/$current_time
#mkdir $curr_res_dir
#touch $curr_res_dir/res.txt 
touch $curr_res_file

#Get benchmark batch limit
if [ $# -ge 1 ]; then
    if [ "$1" -ne 0 ]; then
       echo $1 
    fi
fi


while IFS= read -r filename; do
  file="$PREPROC_BENCHMARK_HOME${filename}"
  echo "Processing: $file"

  #Run solvers
  echo "Run cvc5 without rewrites..."
  call_cvc5_without_rewrite $file

  echo "Run cvc5 with rewrites..."
  call_cvc5_rewrite $file

  echo "Run veriT..."  

  #If any error was detected save file in Error/ directory and add to Error/log.txt

  #Delete processed benchmarks from file
done < "$PROBLEM_LOG"
