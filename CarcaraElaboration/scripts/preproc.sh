#!/bin/bash
source config

timeout_sec=1
delete_lets=true
verbose_mode=false
limit_amount=false
delete_bench=false
nr_large=0

usage() {
 echo "Usage: $0 [OPTIONS]"
 echo "Options:"
 echo " -h       | --help            Display this help message"
 echo " -v       | --verbose         Enable verbose mode"
 echo " -t <nr>  | --timeout <nr>    Change timeout limit (default: 1s)"
 echo " -l <nr>  | --limit <nr>      Only preprocess <nr> benchmarks and then stop (default: all are run). Note that already preprocessed benchmarks are not deleted!"
 echo " -d       | --delete_bench    This deletes preprocessed benchmarks from /input. Default: false"
 echo " -n       | --no_let          Don't delete lets (default: false, i.e. lets are not deleted)"
}

handle_options() {

#Reduce long options to short ones
for arg in "$@"; do
  shift
  case "$arg" in
    '--help')   set -- "$@" '-h'   ;;
    '--verbose')   set -- "$@" '-v'   ;;
    '--timeout')   set -- "$@" '-t'   ;;
    '--limit')   set -- "$@" '-l'   ;;
    '--delete_bench')   set -- "$@" '-d'   ;;
    '--no_let')   set -- "$@" '-n'   ;;
    *)          set -- "$@" "$arg" ;;
  esac
done

while getopts "hvl:t:nd" flag; do

 case $flag in
   h)
   usage
   exit 0
   ;;
   v)
   verbose_mode=true
   ;;
   n)
   delete_lets=false
   ;;
   l)
   limit_amount=true
   run_amount=${OPTARG}
   limit=$run_amount
   ;;
   t)
   timeout_sec=${OPTARG}
   ;;
   d)
   delete_bench=true
   ;;
   \?)
   usage
   exit -1
   ;;
 esac
done
}

write_problem() {
  delete_lets=$1
  output_file=$2
  file=$3

  cp $file $PREPROC_BENCHMARK_HOME
  echo "$output_file" >> $PROBLEM_LOG
}

test_result()
{

  file=$1
  output_file=$2
  delete_lets=$3
  if $delete_lets;
  then
    verbose_msg "Delete lets using cvc5"
    cvc5_new_problem=$(timeout $timeout_sec $CVC5_HOME -o raw-benchmark --parse-only --dag-thresh=0 "$file" | sponge "$file")
  fi
  
  verbose_msg "Run verit"
  verit="$($VERIT_SOLVER --proof-prune --proof-merge --proof-with-sharing --proof-define-skolems --disable-banner --proof=- -s  $file 2>&1)"
  return_value=$?
  max_nr_lines=1500

  if [[ $return_value = 124 ]] ; 
  then 
    echo "Timeout $file"
    return 124
  elif [[ $return_value = 1 ]] ;
  then 
    echo "Solver $solver_name$ could not solve problem!"
    return -1
  elif [[ $verit == *"(error "* ]] ;
    then 
    echo "Solver $solver_name$ could not solve problem! Some error occurred"
    return -1
  elif [[ $verit == *"unknown"* ]] ;
    then 
    echo "Solver $solver_name$ could not solve problem! Unkown result"
    return -1 
  elif [[ $(echo "$verit" | wc -l) -ge $max_nr_lines ]] ;
    then 
    echo "Proof is too big."
    cp $file $PREPROC_LARGE_BENCHMARK_HOME
    return 3
  else
    if $verbose_mode ; then nr_processed=$(($nr_processed+1)); fi;
    echo "Proof could be generated, copy benchmark"
    write_problem $delete_lets $output_file $file
  fi;

  return 0
 }
 
verbose_msg() {
  if [ "$verbose_mode" = true ] ; then echo $1; fi
}

handle_options "$@" 

> $PROBLEM_LOG

if $verbose_mode ; then nr_files=$(find "$INPUT_BENCHMARK_HOME" -type f -name "*.smt2" | wc -l); nr_processed=0; fi;

#Carcara sometimes generates benchmarks with .lia_smt2 extension
#for file in $INPUT_BENCHMARK_HOME/*.lia_smt2; do
#    mv -- "$file" "${file%.lia_smt2}.smt2"
#done

# Find all .smt2 files recursively in the given directory
find $INPUT_BENCHMARK_HOME -type f -name "*.smt2" | while read -r file; do
  if $verbose_mode ; then echo "Preprocessing: $file"; fi;
  # Run a command on each file and store the output in Preprocessed/ folder
  output_file="$PREPROC_BENCHMARK_HOME/$(basename "$file")"
  res=0

  # Check if the file contains the string "(set-info :status sat)"
  if ! grep -q "(set-info :status sat)" "$file";
  then
    verbose_msg "Run verit without proofs"
    verit=$(timeout $timeout_sec $VERIT_SOLVER $file 2>&1)
    
    if [ $? -ne 124 ] ;
    then
      test_result $file $output_file $delete_lets
      res=$?
      if [ $res = 3 ] ;
      then
       nr_large=$(($nr_large+1));
      fi;
    else
      verbose_msg "Found sat bench"
    fi;  
  fi;

  if $delete_bench ;
  then
    if [ $res = 3 ] ;
    then
      echo $file
      cp $file $PREPROC_LARGE_BENCHMARK_HOME 
    fi;
    rm $file;
  fi;
    
  if $limit_amount ; 
  then 
    run_amount=$(($run_amount-1));
    if [[ $run_amount = 0 ]];
    then
      verbose_msg "Finished pre-processing."
      verbose_msg "Found $nr_files files. "
      verbose_msg "I preprocessed $limit files."
      verbose_msg "Of these, "$nr_processed" files remain after preprocessing."; 
      verbose_msg "nr_large $nr_large"
      break;
    fi;
  fi;
done
  

if [ "$limit_amount" = false ] ;
then 
  verbose_msg "Finished pre-processing."
  verbose_msg "Found $nr_files files. "
  verbose_msg "I processed all of these. Of these "$nr_processed" files remain after preprocessing."; 
  verbose_msg "nr_large $nr_large"
fi

if $delete_bench 
then verbose_msg "I deleted all files I preprocessed"; 
else verbose_msg "I did not delete the files I preprocessed"; 
fi;



