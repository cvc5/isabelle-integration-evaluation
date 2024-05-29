#!/bin/bash

source config

timeout_sec=2
run_verit=true
delete_lets=true
verbose_mode=false
save_pre_image=false
limit_amount=false
delete_bench=false
small_proofs=true

usage() {
 echo "Usage: $0 [OPTIONS]"
 echo "Options:"
 echo " -h       | --help            Display this help message"
 echo " -v       | --verbose         Enable verbose mode"
 echo " -t <nr>  | --timeout <nr>    Change timeout limit (default: 2s)"
 echo " -l <nr>  | --limit <nr>      Only preprocess <nr> benchmarks and then stop (default: all are run). Note that already preprocessed benchmarks are not deleted!"
 echo " -d       | --delete_bench    This deletes preprocessed benchmarks from /input. Default: false"
 echo " -s       | --no_verit        Don't run verit (default: false, i.e. veriT is run)"
 echo " -n       | --no_let          Don't delete lets (default: false, i.e. lets are not deleted)"
 echo " -c <dir> | --compress <dir>  compress and store preprocessed benchmarks in directory"
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
    '--no_verit')   set -- "$@" '-s'   ;;    
    '--no_let')   set -- "$@" '-n'   ;;
    '--compress')   set -- "$@" '-c'   ;;  
    *)          set -- "$@" "$arg" ;;
  esac
done

while getopts "hvsl:t:c:nd" flag; do

 case $flag in
   h)
   usage
   exit 0
   ;;
   v)
   verbose_mode=true
   ;;
   s)
   run_verit=false
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
   c)
   save_pre_image=true
   pre_image_name=${OPTARG}
   ;;
   \?)
   usage
   exit -1
   ;;
 esac
done
}

test_proof()
{

  file=$1
  
  verbose_msg "Run cvc5 with proofs enabled"
  cvc5="$(timeout 4 $CVC5_HOME --proof-format-mode=alethe --dump-proofs --dag-thres=0 --produce-proofs --proof-granularity=dsl-rewrite --proof-define-skolems --full-saturate-quant --no-stats --sat-random-seed=1 --lang=smt2 $file 2>&1)"
  return_value=$?
  max_nr_lines=1500

  if [[ $return_value = 124 ]] ; 
  then 
    echo "Timeout $file"
    return 124
  elif [[ $return_value = 1 ]] ;
  then 
    echo "cvc5 could not solve problem in time limit when producing proofs!"
    return -1
  elif [[ $cvc5 == *"error "* ]] ;
    then 
    echo "cvc5 could not solve problem! Some error occurred"
    return -1
  elif [[ $cvc5 == *"unknown"* ]] ;
    then 
    echo "cvc5 could not solve problem! Unkown result"
    return -1 
  elif [[ $(echo "$cvc5" | wc -l) -ge $max_nr_lines ]] ;
    then 
    echo "Proof is too big."
    return 3
  else
    echo "Proof could be generated, copy benchmark"
    return 0
  fi;
 }
 
write_problem() {
  if $small_proofs ;
  then
    test_proof "$file"
    if [ $? -ne 0 ] ;
    then too_big=true ;
    else too_big=false ;
    fi;
  else
    too_big=false
  fi;
  
  echo $file
  
  if ! $too_big ;
  then
   if $1 ;
   then
     output_file="$PREPROC_BENCHMARK_HOME$(basename "$file")"
     cvc5_new_problem=$(timeout $timeout_sec $CVC5_HOME -o raw-benchmark --parse-only --dag-thresh=0 "$file" > "$output_file")
   else
     cp $file $PREPROC_BENCHMARK_HOME ;
   fi;
 fi;
}


 
verbose_msg() {
  if [ "$verbose_mode" = true ] ; then echo $1; fi
}

handle_options "$@" 

if $verbose_mode ; then nr_files=$(find "$INPUT_BENCHMARK_HOME" -type f -name "*.smt2" | wc -l); nr_processed=0; fi;

echo $INPUT_BENCHMARK_HOME
find "$INPUT_BENCHMARK_HOME" -type f -name "*.smt2" | while read -r file; do

  # Check if the file contains the string "(set-info :status sat)"
  if ! grep -q "(set-info :status sat)" "$file";
  then cvc5=$(timeout $timeout_sec $CVC5_HOME --no-stats --sat-random-seed=1 --lang=smt2 $file 2>/dev/null)
    if [ $? -ne 124 ] ;
    then
      write_problem $delete_lets
      if $verbose_mode ; then nr_processed=$(($nr_processed+1)); fi;
    else
      if $run_verit ;
      then
        #In case cvc5 times out we still want to run veriT in case it can solve the goal to be fair
        verit=$(timeout $timeout_sec $VERIT_HOME --disable-banner $file)
        if [ $? -ne 124 ] ;
        then
	  write_problem $delete_lets
          if $verbose_mode ; then nr_processed=$(($nr_processed+1)); fi;
        fi;
      else
      	if $verbose_mode ; then nr_processed=$(($nr_processed+1)); fi;
      fi;
    fi;
  fi;

  if $delete_bench ;
  then
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
      break;
    fi;
  fi;
done
  

if [ "$limit_amount" = false ] ;
then 
  verbose_msg "Finished pre-processing."
  verbose_msg "Found $nr_files files. "
  verbose_msg "I processed all of these. Of these "$nr_processed" files remain after preprocessing."; 
fi

if $delete_bench 
then verbose_msg "I deleted all files I preprocessed"; 
else verbose_msg "I did not delete the files I preprocessed"; 
fi;
      
#Very brittle: Make better
if $save_pre_image ; then cd $PREPROC_BENCHMARK_HOME; tar -cvf "$PREPROC_IMAGE_BENCHMARK_HOME$pre_image_name.tar" "preprocessed/"; cd $BASE_DIR; fi
