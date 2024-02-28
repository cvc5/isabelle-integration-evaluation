#!/bin/bash

source config

timeout_sec=1

#For all files that are not marked as sat
grep -L "(set-info :status sat)" "$INPUT_BENCHMARK_HOME"* | while IFS= read -r file; do
  #TODO: Use cvc5's timeout? But then I cannot check the exit code I think
  cvc5=$(timeout $timeout_sec $CVC5_HOME --no-stats --sat-random-seed=1 --lang=smt2 $file)
  if [ $? -ne 124 ] ; then
    cp $file $PREPROC_BENCHMARK_HOME
    echo "Copied $file"
  fi
done
