#!/bin/bash

if ! [ $# -ge 4 ]; then
    echo "Usage: $0 <solver_config (cpc, cvc5, cvc5_without_rewrite, or verit)> <benchmark library name> <base_dir> <input_file> <optional: timeout>"
    exit 1
fi

timeout_sec=300s
CVC5_HOME=/barrett/scratch/lachnitt/Binaries/cvc5bin
VERIT_HOME=/barrett/scratch/lachnitt/Binaries/verit/veriT
remove=false

Help()
{
   # Display Help
   echo "Run a solver (cpc, cvc5, cvc5_without_rewrite or verit) on a benchmark"
   echo
   echo "options:"
   echo "t     Set timeout for solving and producing proof"
   echo "h     Print this Help."
   echo
}

while getopts ":ht:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      t) timeout_sec=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done


#Read positional arguments
shift $((OPTIND - 1))

solver_config=$1
bench_lib=$2
base_dir=$3


if [ $# -eq 5 ]; then
  timeout_sec=$4
  input_file=$5
  echo "timeout $timeout_sec"
else
  input_file=$4
fi




echo "Nr args $#"

echo "Input_file $input_file"


filename_raw=$(basename -- "$input_file")
new_file="${filename_raw%.*}"
result_file_proof="$new_file.alethe"
#result_file_problem="$new_file.smt2"
base_dir="${base_dir%/}"
path=$(echo "$input_file" | sed "s|^$base_dir||")
path="${path#//}"
set_name="${path%/*}"
set_name="${set_name#/}"
echo "problem_path: $base_dir/$path"
temp="${path%/*}"
echo "relative_benchmark_path: $temp/"
echo "proof_name: $result_file_proof"
str="json: {\"benchmark_name\": \"$(basename $input_file)\", \"benchmark_path\": \"$input_file\", \"relative_benchmark_path\":\"$path\",\"library_name\": \"$bench_lib\", \"set_name\": \"$set_name\", \"solving\": [{\"solver_config\": \"$solver_config\" ,\"solving_outcome\": "
echo -n $str



#Run solvers
if [ $solver_config = "cvc5" ];
then
  start_time=$(date +%s%N)
  output=$(timeout $timeout_sec $CVC5_HOME --proof-prune-input --proof-mode=full-proof-strict --proof-format-mode=alethe --dump-proofs --produce-proofs --proof-granularity=dsl-rewrite --proof-alethe-define-skolems --proof-elim-subtypes --full-saturate-quant --no-stats --sat-random-seed=1 --lang=smt2  $input_file 2>&1 )
  return_value=$?
  end_time=$(date +%s%N)
  solver_name="cvc5"
  solver_config="cvc5"
elif [ $solver_config = "cpc" ];
then
  start_time=$(date +%s%N)
  output=$(/usr/bin/time timeout $timeout_sec $CVC5_HOME --proof-prune-input --proof-mode=full-proof-strict --proof-format-mode=cpc --dump-proofs --produce-proofs --proof-granularity=dsl-rewrite --proof-elim-subtypes --full-saturate-quant --no-stats --sat-random-seed=1 --lang=smt2  $input_file)
  return_value=$?
  end_time=$(date +%s%N)
  solver_name="cpc"
  solver_config="cpc"
elif [ $solver_config = "verit" ];
then
  start_time=$(date +%s%N)
  output=$(/usr/bin/time  timeout $timeout_sec $VERIT_HOME '--print-cvc5-numbers' '--proof=-' '--proof-prune' '--proof-merge' '--proof-define-skolems' '--disable-banner' '--proof-with-sharing' '-s' $input_file)
  return_value=$?
  exec 4>&-
  end_time=$(date +%s%N)
  solver_name="verit"
  solver_config="verit"
else echo "\"invalid solver config\"}]}"; exit -1; fi;
    

#echo "output $output"
#Write output

  if ! [ $return_value = 0 ] ; 
  then 
    ret=-1
  elif [ -z "$output" ] ;
  then
    ret=-1
  elif [[ $output == *"unknown"* ]]
  then 
    ret=-3
  elif [[ $output == *"(error "* ]] ;
  then
    ret=-4
  elif [[ $output == "sat"* ]] ;
  then
    ret=-2
  else

    touch $result_file_proof
    #touch $result_file_problem
    echo "$output">$result_file_proof
    #cat "$input_file">$result_file_problem

    elapsed_time_old=$((end_time - start_time))

    ret=0
    out_dir=$(basename $base_dir)
    nr_of_lines=$(cat $result_file_proof | grep -c -E "^\((assume|step|anchor)") # ignore define-fun

    more=", \"nr_of_lines\": $nr_of_lines, \"solving_time\": \"$elapsed_time_old\","
    more=$more" \"proof_path\": \"$filename_raw.alethe\""
  fi
  
  echo " "$ret$more"}]}" 
  echo "outcome: $ret"
