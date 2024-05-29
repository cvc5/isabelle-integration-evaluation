#!/bin/bash

source config

benchmark_limit=20
verbose_mode=false
stats_dir=misc
more_stats=false
delete_timeouts=false

usage() {
 echo "Usage: $0 [OPTIONS]"
 echo "Options:"
 echo " -h          | --help             Display this help message"
 echo " -v          | --verbose          Enable verbose mode"
 
 echo " -d  <dir>   | --out_dir <dir>    name of the directory you want to save the statistic files to (default: saved in misc)"
 echo " -t   collect additional statistics"
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
    *)          set -- "$@" "$arg" ;;
  esac
done

while getopts "hvd:t" flag; do
 case $flag in
   h)
   usage
   exit 0
   ;;
   v)
   verbose_mode=true
   ;;
   d)
   stats_dir=("$OPTARG")
   ;;
   t)
   more_stats=true;
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
  output=$(eval "timeout 20 $solver_command" 2>&1)
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
  elif [[ $output == *"error"* ]] ;
    then 
    echo "Solver $solver_name could not solve problem! Some error occurred"
    write_json $new_file $solver_name "-3" "$stats"
    return -1
  elif [[ $output == *"WARN"* ]] ;
    then 
    echo "Solver $solver_name gave warning"
    write_json $new_file $solver_name "-3" "$stats"
    return -1
  elif [[ $output == *"unknown"* ]] ;
    then 
    echo "Solver $solver_name$ could not solve problem! Unkown result"
    rm $file
    write_json $new_file $solver_name "-1" "$stats"
    return -1 
  else
  echo "I sould not be in here $new_file"
    # Make proof file
    new_file="${new_file%.*}"  
    resultFile="$BENCHMARK_HOME/$new_file""_elaborated.alethe";
    touch $resultFile
    echo "unsat" >$resultFile;
    echo "$output">>$resultFile;

    # Duplicate problem file
    new_problem_file="$BENCHMARK_HOME/$new_file""_elaborated.smt2"
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

call_carcara()
{
  problem_file=$1
  new_file="${problem_file%.*}"  
  proof_file="$new_file.alethe";

  local carcara="$CARCARA_HOME elaborate $proof_file $problem_file --lia-solver cvc5 --ignore-unknown-rules --no-print-with-sharing --lia-solver-args \"--tlimit=10000 --lang=smt2 --proof-format-mode=alethe --proof-alethe-res-pivots --dag-thres=0 --proof-elim-subtypes --print-arith-lit-token\"" 

  write_result "carcara" "$carcara" "_elaborated" $problem_file;
  return $?
}

handle_options "$@"
solvers="carcara"

if [ -z "$solvers" ]; then
    echo "No solvers set"
    exit -1
fi

echo "Run carcara on the next $benchmark_limit benchmarks"

#Make result directory
current_time=$(date "+%Y.%m.%d-%H.%M.%S")
mkdir -p $EVAL_RES$stats_dir/
mkdir -p $EVAL_RES$stats_dir/"Elaborator/"
curr_res_file=$EVAL_RES$stats_dir/"Elaborator/"$current_time".json"
touch $curr_res_file
echo '['>> $curr_res_file
 
 
find $BENCHMARK_HOME -type f -name "*.smt2" | while read -r file; do

  if $verbose_mode ; then echo "Elaborating: $file"; fi;

  timeout=false
  error=false

  if $verbose_mode ; then echo "Run carcara ..."; fi;
  call_carcara $file
  retval=$?
  if [ $retval == 124 ]; then timeout=true; fi;
  if [ $retval == 255 ]; then error=true; fi;

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


if $delete_timeouts 
then verbose_msg "I deleted files that timed out or gave an error from /preprocessed"; 
else verbose_msg "I did not delete the files that times out or gave an error /preprocessed"; 
fi;


