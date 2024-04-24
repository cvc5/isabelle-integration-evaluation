#!/bin/bash

source config

verbose_mode=false
verit=false
cvc5_with_rewrite=false
cvc5_without_rewrite=false
stats_dir=misc


usage() {
 echo "Usage: $0 [OPTIONS]"
 echo "Options:"
 echo " -h   Display this help message"
 echo " -v   Enable verbose mode"
 echo " -s   solvers that should be used (verit,cvc5_without_rewrite,cvc5_with_rewrite). Use multiple -s arguments if you want to use more than one solver"
 echo " -d   name of the directory you want to save the statistic files to (default: saved in misc)"
}

handle_options() {
while getopts "hvs:d:w" flag; do
 case $flag in
   h)
   usage
   exit 0
   ;;
   v)
   verbose_mode=true
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
   w)
   words=true
   ;;
   \?)
   usage
   exit -1
   ;;
 esac
done
}


# Main

handle_options "$@" 
mkdir -p $EVAL_RES$stats_dir/
mkdir -p $EVAL_RES$stats_dir/"Checker/"

#build HOL-CVC to avoid timeout below
#I think this will not rebuild if already build but double check
#This is now done in setupIsabelle.sh
#if $words then $ISABELLE_BIN build -d $ISABELLE_HOME/src/HOL/ HOL-CVC-Word else $ISABELLE_BIN build -d $ISABELLE_HOME/src/HOL/ HOL-CVC

for solver in "${solvers[@]}"; do
  echo "Checking proofs by solver: $solver"
  current_time=$(date "+%Y.%m.%d-%H.%M.%S")
  curr_res_file=$EVAL_RES$stats_dir/"Checker/"$current_time".json"

  rm -f $ISABELLE_USER_HOME/$solver
  
  # Run Isabelle on theory
  timeout 500s "$ISABELLE_BIN" build -c -d "$ISABELLE_BASE/ReconstructionEvaluation$solver/" "EvaluateReconstruction$solver"
  if [ $? = 124 ] ; 
  then echo "Isabelle was interrupted. Increase time limit.";
  fi;
  #Copy result vom Isabelle run to Result directory

  cp $ISABELLE_USER_HOME/$solver $curr_res_file

  sed -i '1s/^/[\n/' $curr_res_file
  #Delete the last comma
  if [ $(wc -l < $curr_res_file) -gt 1 ]; then
    sed -i '$s/.$//' "$curr_res_file"
  fi

  echo ']'>> $curr_res_file

  #TODO: Remove the file?
  rm -f $ISABELLE_USER_HOME/$solver
done


