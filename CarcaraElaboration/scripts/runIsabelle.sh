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

timeout 500s $ISABELLE_BIN build -c -d "$ISABELLE_BASE" "EvaluateReconstruction"

#Copy result vom Isabelle run to Result directory


cp $ISABELLE_USER_HOME/"carcara" $curr_res_file

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



