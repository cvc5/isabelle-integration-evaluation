#!/bin/bash
source config

if [ $# -eq 0 ]; then
    echo "Usage: $0 <output directory> (<input_dir(default is /input)>)"
    exit 1
fi

if [ $1 = "-h" ]; then
    echo "Usage: $0 <output directory> (<input_dir(default is /input)>)"
    exit 1
fi

input_dir=$INPUT_BENCHMARK_HOME
if [ $# -eq 2 ]; then
  input_dir=$2
fi


rm -f "$Result_BENCHMARK_HOME/cvc5_without_rewrite/"*;

echo "prepare isabelle"
word_str=""
(eval "$SCRIPTS_HOME/util/setupIsabelle.sh $word_str")
$ISABELLE_BIN build -d $ISABELLE_HOME/src/HOL/ HOL-CVC ;

echo "Process benchmarks"

stats_name=$1
stats_dir=$EVAL_RES/$stats_name
mkdir -p $stats_dir
mkdir -p "$stats_dir/Checker"

mkdir -p "$stats_dir/Bench"
bench_general_file="$stats_dir/Bench/all_bench.json"
echo "" > $bench_general_file
batch=0



process_benchmark()
{
  current_time=$(date "+%Y.%m.%d-%H.%M.%S")
  curr_res_file=$stats_dir/"Checker"/$current_time".json"
  echo "Save results to $curr_res_file";

  # Run Isabelle on theory
  rm -f $ISABELLE_USER_HOME/"cvc5_without_rewrite/"
  
  res=$(timeout 300s $ISABELLE_BIN build -c -d "$ISABELLE_BASE/ReconstructionEvaluationcvc5_without_rewrite/" "EvaluateReconstructioncvc5_without_rewrite" 2>&1)
  error_code=$?
  echo $res
  #Copy result vom Isabelle run to Result directory
  cp $ISABELLE_USER_HOME/"cvc5_without_rewrite" $curr_res_file
    
  sed -i '1s/^/[\n/' $curr_res_file
  #Delete the last comma
  if [ $(wc -l < $curr_res_file) -gt 1 ]; then
    sed -i '$s/.$//' "$curr_res_file"
  fi
  sed -i -e '$a\'$'\n'']' $curr_res_file
     
  rm -f "$Result_BENCHMARK_HOME/cvc5_without_rewrite/"*;
}   

while read -r problem_file; do

  file_without_extension="${problem_file%.*}"
  echo "Processing $(basename $file_without_extension)"
  file_with_alethe=$file_without_extension".alethe"
  echo "file_with_alethe $file_with_alethe"
  if [ -e $file_with_alethe ]
  then
    batch=$(($batch+1))
    cp $problem_file "$Result_BENCHMARK_HOME/cvc5_without_rewrite/"
    cp $file_with_alethe "$Result_BENCHMARK_HOME/cvc5_without_rewrite/"
    $SCRIPTS_HOME/util/writeGeneralBenchInfoToJson.sh $bench_general_file $(basename $file_without_extension)".smt2" $problem_file true ""

  fi  
      
  if [ $batch = 30 ];
  then
    process_benchmark
    batch=0
  fi; 
done <<< $(find "$input_dir" -type f -name "*.smt2")

if [ $batch -ne 0 ];
then
  process_benchmark
fi;

echo "last char $(tail -c 1 $bench_general_file)"
if [ "$(tail -c 1 $bench_general_file)" = "," ]; then
    truncate -s -1 filename.txt
fi

sed -i '1s/^/[\n/' $bench_general_file
#Delete the last comma
if [ $(wc -l < $bench_general_file) -gt 1 ]; then
  sed -i '$s/.$//' "$bench_general_file"
fi
sed -i -e '$a\'$'\n'']' $bench_general_file


python3 $SCRIPTS_HOME/py/combineChecker.py $stats_name

echo "Done with all benchmarks"
echo "Delete all files"
rm -f "$Result_BENCHMARK_HOME/cvc5_without_rewrite/"*;

> $PROBLEM_LOG
