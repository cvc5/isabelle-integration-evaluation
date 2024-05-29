#!/bin/bash
#Expert script, just for convenience
source config

timeout_sec=2

usage() {
 echo "Usage: $0 [OPTIONS]"
 echo "Options:"
 echo " -h       | --help            Display this help message"
 echo "This is an expert script"
}

handle_options() {

#Reduce long options to short ones
for arg in "$@"; do
  shift
  case "$arg" in
    '--help')   set -- "$@" '-h'   ;;
    *)          set -- "$@" "$arg" ;;
  esac
done

while getopts "hvsl:t:c:nd" flag; do

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


handle_options "$@" 

nr_removed=0
echo $PREPROC_BENCHMARK_HOME
find "$PREPROC_BENCHMARK_HOME" -type f -name "*.smt2" | while read -r file; do
  echo $nr_removed
  res="timeout 10 $CVC5_HOME --proof-format-mode=alethe --dump-proofs --dag-thres=0 --produce-proofs --proof-granularity=dsl-rewrite --proof-define-skolems --full-saturate-quant --no-stats --sat-random-seed=1 --lang=smt2 $file"
  output=$($res > /dev/null 2>&1)
  return_value=$?
  
  if [ $return_value = 124 ] ; 
  then 
    echo "Timeout $file"
    ((nr_removed=nr_removed+1))
    rm $file
  elif [ $return_value = 1 ] ;
  then 
    echo "Solver $solver_name$ could not solve problem!"
    ((nr_removed=nr_removed+1))
    rm $file
  elif [[ $output == *"(error "* ]] ;
    then 
    echo "Solver $solver_name$ could not solve problem! Some error occurred"
    ((nr_removed=nr_removed+1))
    rm $file
  fi;
done

echo "Removed $nr_removed bechmarks"
