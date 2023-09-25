#!/bin/bash

BENCHMARK_HOME=./Benchmark
PROOF_HOME=./AletheProofs
CVC5_HOME=/barrett/scratch/lachnitt/Sources/cvc5/build/bin/cvc5


if [ $# -ne 0 ]
  then
    max_files=$1
    nr_files=0
fi


for file in "$BENCHMARK_HOME"/*.smt2 ; do

  cvc5=$(timeout 12 $CVC5_HOME --proof-format-mode=alethe --dump-proofs --produce-proofs --proof-granularity=dsl-rewrite --simplification=none --lang=smt2 --full-saturate-quant --no-stats --sat-random-seed=1 --lang=smt2 --dag-thres=0 $file)
  if [ $? = 124 ] ; then
    rm $file
  elif [ `echo $cvc5 | grep -c "unsat" ` -gt 0 ]
  then
    new_file="${file##*/}"  
    new_file="${new_file%.*}"  
    resultFile=$PROOF_HOME/$new_file.alethe;
    touch $resultFile
    echo "$cvc5">$resultFile;
  else
    rm $file
  fi
  
  if [ $# -ne 0 ]
    then
      nr_files=$((nr_files+1))
      if [ $nr_files -eq $max_files ]
        then
	  exit
      fi
  fi
done
