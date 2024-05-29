#!/bin/bash
source config

verbose_mode=false
delete_mode=false
stats_dir=$RESULT_HOME/misc

usage() {
 echo "Usage: $0 [OPTIONS]"
 echo "Options:"
 echo " -h   Display this help message"
 echo " -v   Enable verbose mode"
 echo " -f   Delete benchmarks after processing"
 echo " -d   name of the directory in Result you want to save the statistic files to (default: saved in Result/misc)"
}

handle_options() {
while getopts "hvd:f" flag; do
 case $flag in
   h)
   usage
   exit 0
   ;;
   v)
   verbose_mode=true
   ;;
   d)
   stats_dir=("$RESULT_HOME/$OPTARG")
   ;;
   f)
   delete_mode=true
   ;;
   \?)
   usage
   exit -1
   ;;
 esac
done
}

handle_options "$@" 

mkdir -p $stats_dir
current_time=$(date "+%Y.%m.%d-%H.%M.%S")
curr_res_file=$stats_dir/$current_time".json"
if $verbose_mode ; then echo "Save results to $curr_res_file"; fi;

# Run Isabelle on theory
rm -f $ISABELLE_USER_HOME/"carcara"
incomplete_run=false

res=$(timeout 200s $ISABELLE_BIN build -c -d "$ISABELLE_BASE" "EvaluateReconstruction" 2>&1)
error_code=$?
echo $res
#Copy result vom Isabelle run to Result directory
cp $ISABELLE_USER_HOME/"carcara" $curr_res_file

if [ $error_code = 124 ]; then
  echo "Isabelle timed out. Delete last benchmark (and its elaborated or non-elaborated form) from input, preprocessed. "
  echo "This could also happen because of a too low time limit and not because of a specific benchmark so be aware"
  incomplete_run=true
  last_line=$(tail -n 1 $curr_res_file)
  echo "here"
  benchmark_name=$(echo $last_line | sed -n 's/.*"benchmark_name": "\([^"]*\)".*/\1/p')
  echo "offending benchmark was $benchmark_name"
  #delete imcomplete entry
  sed -i '$ d' $curr_res_file
  echo "INPUT_BENCHMARK_HOME $INPUT_BENCHMARK_HOME"
  if [[ $benchmark_name == *_elaborated.smt2 ]]; then
      cropped_bench="${benchmark_name%_elaborated.smt2}.smt2"
      echo "cropped: $cropped_bench"
      echo "path $INPUT_BENCHMARK_HOME/$cropped_bench"
      rm $INPUT_BENCHMARK_HOME/$cropped_bench
      rm $PREPROC_BENCHMARK_HOME/$cropped_bench
      rm $PREPROC_BENCHMARK_HOME/$benchmark_name
  else
      echo "path $INPUT_BENCHMARK_HOME/$benchmark_name.smt2"
      rm $INPUT_BENCHMARK_HOME/$benchmark_name
      cropped_bench="${benchmark_name%.smt2}_elaborated.smt2"
      echo "cropped: $cropped_bench"
      rm $PREPROC_BENCHMARK_HOME/$cropped_bench
      rm $PREPROC_BENCHMARK_HOME/$benchmark_name
  fi
  echo "done with offending benchmark"
fi;
 


  sed -i '1s/^/[\n/' $curr_res_file
  #Delete the last comma
  if [ $(wc -l < $curr_res_file) -gt 1 ]; then
    sed -i '$s/.$//' "$curr_res_file"
  fi

  sed -i -e '$a\'$'\n'']' $curr_res_file

if $delete_mode ; then
  if $verbose_mode ; then echo "Delete processed benchmarks"; fi;
  rm -f "$BENCHMARK_HOME/*";
fi;

#if [ $incomplete_run ]; then return 1; fi;

