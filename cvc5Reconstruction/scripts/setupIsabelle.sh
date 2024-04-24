#!/bin/bash

source config
words=false

usage() {
 echo "Usage: $0 [OPTIONS]"
 echo "Options:"
 echo " -h   Display this help message"
 echo " -b   if you want to check bv problems (deactivated by default since it takes forever to load SMT_CVC_Word). You'll also have to run the script that writes the theories again"
}

handle_options() {
while getopts "hb" flag; do
 case $flag in
   h)
   usage
   exit 0
   ;;
   b)
   words=true
   ;;
   \?)
   usage
   exit -1
   ;;
 esac
done
}

write_theory()
{
  solver_config=$1
  if [ "$solver_config"="cvc_with_rewrite" ] || [ "$solver_config"="cvc5_without_rewrite" ] ; then solver="cvc5"; else solver="verit"; fi
  theory_file=$ISABELLE_THEORY_BASE/"ReconstructionEvaluation$solver_config/thys/ReconstructionEvaluation$solver_config.thy"
  echo "theory ReconstructionEvaluation$solver_config" > $theory_file
  
  if $words;
  then echo "  imports \"HOL-CVC.SMT_CVC_Word\"" >> $theory_file;
  else echo "  imports \"HOL-CVC.SMT_CVC\"" >> $theory_file; fi
  
  echo $'begin\n' >> $theory_file

  echo "declare [[smt_statistics_file=\"$solver_config\"]]" >> $theory_file
  echo "declare [[smt_verbose=false,smt_trace=false,smt_debug_verit=false,smt_timeout=1.0,smt_reconstruction_step_timeout=1.0]]" >> $theory_file
  echo "declare[[smt_rec_evaluation]]"
  echo "check_smt_dir (\"$solver\") \"/home/lachnitt/Sources/isabelle-integration-evaluation/cvc5Reconstruction/data/benchmarks/$solver_config/\"" >> $theory_file

  echo "end" >> $theory_file
}

# Main

handle_options "$@" 
if $words
then $ISABELLE_BIN build -d $ISABELLE_HOME/src/HOL/ HOL-CVC ;  #TODO: make session for word
else $ISABELLE_BIN build -d $ISABELLE_HOME/src/HOL/ HOL-CVC; fi

  # Write Isabelle theory
  # Only necessary once with the current set-up... Could put whole file path in there but don't want to jepardize system security, easy to mess up 
write_theory "cvc5_with_rewrite"
write_theory "cvc5_without_rewrite"
