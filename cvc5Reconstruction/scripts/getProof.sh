#!/bin/bash

source config

benchmark_limit=50
verbose_mode=false
verit=false
cvc5_with_rewrite=false
cvc5_without_rewrite=false
stats_dir=misc
more_stats=false
delete_timeouts=false
save_pre_image=false
max_proof_steps=false
limit_steps=1500

usage() {
 echo "Usage: $0 [OPTIONS]"
 echo "Options:"
 echo " -h          | --help             Display this help message"
 echo " -v          | --verbose          Enable verbose mode"
 echo " -l <nr>     | --batch_size <nr>  Benchmark processing batch size (default: 50)"
 echo ""
 
 echo "Solver options:"
 echo " -s <solver> | --solver <solver>  , with <solver> in {verit,cvc5_without_rewrite,cvc5_with_rewrite}"
 echo "                                  solvers that should be used. Use multiple -s arguments if you want to use more than one solver"
 echo " -a          | --all              Run all available solvers"
 echo ""
 
 echo " -d  <dir>   | --out_dir <dir>    name of the directory you want to save the statistic files to (default: saved in misc)"
 echo " -t   collect additional statistics"
 echo " -r   delete benchmarks for which at least one solver times out from preprocessed folder"
 echo " -c   compress and store preprocessed benchmarks in directory"
 echo " -k   delete benchmarks that have more than 1500 steps"
 echo ""
}

handle_options() {

#Reduce long options to short ones
for arg in "$@"; do
  shift
  case "$arg" in
    '--help')   set -- "$@" '-h'   ;;
    '--verbose')   set -- "$@" '-v'   ;;
    '--timeout')   set -- "$@" '-t'   ;;
    '--no_verit')   set -- "$@" '-s'   ;;    
    '--no_let')   set -- "$@" '-n'   ;;
    '--compress')   set -- "$@" '-c'   ;;  
    '--limit')   set -- "$@" '-l'   ;;
    *)          set -- "$@" "$arg" ;;
  esac
done

while getopts "hvl:s:d:atrc:k" flag; do
 case $flag in
   h)
   usage
   exit 0
   ;;
   v)
   verbose_mode=true
   ;;
   l)
   benchmark_limit=${OPTARG}
   ;;
   k)
   max_proof_steps=${OPTARG}
   ;;
   a)
   solvers="all solvers: cvc5_with_rewrite, cvc5_without_rewrite, verit"
   cvc5_without_rewrite=true;
   cvc5_with_rewrite=true;
   verit=true;
   ;;
   s)
   solvers+=("$OPTARG")
   if [ $OPTARG = "cvc5_without_rewrite" ]; then cvc5_without_rewrite=true;
   elif [ $OPTARG = "cvc5_with_rewrite" ]; then cvc5_with_rewrite=true;
   elif [ $OPTARG = "verit" ]; then verit=true;
   else echo "Unsupported Solver! Use one of these: verit, cvc5_without_rewrite, cvc5_with_rewrite."; exit -1; fi
   ;;
   d)
   stats_dir=("$OPTARG")
   ;;
   t)
   more_stats=true;
   ;;
   r)
   delete_timeouts=true;
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

verbose_msg() {
  if [ "$verbose_mode" = true ] ; then echo $1; fi
}

write_json(){
 echo '{"benchmark_name" : "'$1'", "solving": [{"solver_name" : "'$2'", "solving_time" : '$3' '$4'}]}'>> $curr_res_file
 echo ',' >> $curr_res_file
}

write_result()
{
  solver_name=$1
  solver_command=$2
  new_file_ending=$3
  file=$4

  new_file="${file##*/}"

  start_time=$(date +%s%N)
  output=$(eval "timeout 10 $solver_command")
  local return_value=$?
  end_time=$(date +%s%N)

  if [ $return_value = 124 ] ; 
  then 
    echo "Timeout $file"
    write_json $new_file $solver_name "-1" "$stats"
    return 124
  elif [ $return_value = 1 ] ;
  then 
    echo "Solver $solver_name$ could not solve problem!"
    write_json $new_file $solver_name "-2" "$stats"
    return -1
  elif [[ $output == *"unknown"* ]] ;
    then 
    echo "Solver $solver_name$ could not solve problem! Unkown result"
    write_json $new_file $solver_name "-1" "$stats"
    return -1  
  elif [[ $output == *"(error "* ]] ;
    then 
    echo "Solver $solver_name$ could not solve problem! Some error occurred"
    write_json $new_file $solver_name "-3" "$stats"
    return -1
  elif [[ $max_proof_steps ]] && [[ $(echo "$output" | wc -l) -ge $limit_steps ]] ;
    then 
    echo "Solver $solver_name$: proof is too big"
    write_json $new_file $solver_name "-4" "$stats"
    return -1
  else
    # Make proof file
    new_file="${new_file%.*}"  
    resultFile="$Result_BENCHMARK_HOME$solver_name/$new_file.alethe";
    touch $resultFile
    echo "$output">$resultFile;

    # Copy problem file
    new_problem_file="$Result_BENCHMARK_HOME$solver_name/$new_file.smt2"
    cp $file $new_problem_file

    elapsed_time=$((end_time - start_time))
    
    # Collect more statistics if wanted
    if $more_stats ;
    then
     file_size=$(stat -c%s "$resultFile")
     nr_step=$(grep -o '(step' $resultFile | wc -l)
     stats=', "file_size" : '$file_size', "nr_step" : '$nr_step;
    fi;
    write_json $new_file $solver_name $elapsed_time "$stats"
  fi
  
  return 0
 
 }

call_cvc5_with_rewrite()
{
  file=$1
  local cvc5="$CVC5_HOME --proof-format-mode=alethe --dump-proofs --dag-thres=0 --produce-proofs --proof-granularity=dsl-rewrite --proof-define-skolems --full-saturate-quant --no-stats --sat-random-seed=1 --lang=smt2 $file"
  write_result "cvc5_with_rewrite" "$cvc5" "_rewrite" $file;
  return $?
}

call_cvc5_without_rewrite()
{
  file=$1
  local cvc5="$CVC5_HOME --proof-format-mode=alethe --dump-proofs --produce-proofs --proof-define-skolems --full-saturate-quant --no-stats --sat-random-seed=1 --lang=smt2 $file"
  write_result "cvc5_without_rewrite" "$cvc5" "_without_rewrite" $file;
  return $?
}

call_veriT()
{
  file=$1
  local verit="$VERIT_HOME --proof-prune --proof-merge --proof-with-sharing --proof-define-skolems --disable-banner --proof=- -s  $file"
  write_result "verit" "$verit" "_verit" $file;
  return $?
}

handle_options "$@"
delete_timeouts=true
if [ -z "$solvers" ]; then
    echo "No solvers set"
    exit -1
fi

for val in "${solvers[@]}"; do
    echo " - $val"
done
echo "on the next $benchmark_limit benchmarks"

#Make result directory
current_time=$(date "+%Y.%m.%d-%H.%M.%S")
mkdir -p $EVAL_RES$stats_dir/
mkdir -p $EVAL_RES$stats_dir/"Solver/"
curr_res_file=$EVAL_RES$stats_dir/"Solver/"$current_time".json"
touch $curr_res_file
echo '['>> $curr_res_file
 
dir1="$Result_BENCHMARK_HOME"cvc5_with_rewrite
dir2="$Result_BENCHMARK_HOME"cvc5_without_rewrite 
dir3="$Result_BENCHMARK_HOME"verit
mkdir -p $dir1/
mkdir -p $dir2/
mkdir -p $dir3/
 
head -n $benchmark_limit "$PROBLEM_LOG" | while IFS= read -r filename; do
  file="$PREPROC_BENCHMARK_HOME${filename}"
  if $verbose_mode ; then echo "Processing: $file"; fi;

  #Run solvers
  timeout=false
  error=false
  
  if $cvc5_without_rewrite ;
  then
    if $verbose_mode ; then echo "Run cvc5 without rewrites..."; fi;
    call_cvc5_without_rewrite $file
    retval=$?
    if [ $retval == 124 ]; then timeout=true; fi;
    if [ $retval == 255 ]; then error=true; fi;
  fi

  if $cvc5_with_rewrite ;
  then
    if $verbose_mode ; then echo "Run cvc5 with rewrites..."; fi;
    call_cvc5_with_rewrite $file
    retval=$?
    if [ $retval == 124 ]; then timeout=true; fi;
    if [ $retval == 255 ]; then error=true; fi;
  fi
  
  if $verit ;
  then
    if $verbose_mode ; then echo "Run veriT ..."; fi;
    call_veriT $file
    call_cvc5_with_rewrite $file
    retval=$?
    if [ $retval == 124 ]; then timeout=true; fi;
    if [ $retval == 255 ]; then error=true; fi;
  fi

  if $delete_timeouts 
  then
    if $timeout || $error ; 
    then
      echo "Timeout or Error detected for benchmark $filename, deleting it...";
      rm $file; 
    fi;
  fi;
done

#Delete the last comma
if [ $(wc -l < $curr_res_file) -gt 1 ]; then
    sed -i '$s/.$//' "$curr_res_file"
fi

echo ']'>> $curr_res_file
#Delete processed benchmarks from file
sed -i -e 1,"$benchmark_limit"d $PROBLEM_LOG

current_time=$(date "+%Y.%m.%d-%H.%M.%S")
if $save_pre_image ; then
 mkdir -p $BENCHMARK_IMAGE_BENCHMARK_HOME$pre_image_name/$current_time/
 cp -r $Result_BENCHMARK_HOME/* $BENCHMARK_IMAGE_BENCHMARK_HOME$pre_image_name/$current_time/
fi


if $delete_timeouts 
then verbose_msg "I deleted files that timed out or gave an error from /preprocessed"; 
else verbose_msg "I did not delete the files that times out or gave an error /preprocessed"; 
fi;


