#!/bin/bash

PROOF_HOME=./AletheProofs
PROBLEM_HOME=./Benchmark
RESULTS_HOME=./GeneratedProblems
STATS=./Results/FileToRewrite.txt

> $STATS
echo "file_name,rule" >> $STATS
     
delete_files=$1

nr_curr_proofs=$(find "./AletheProofs/" -maxdepth 1 -type f | wc -l)
if [ $nr_curr_proofs -ne 0 ]
then

for proof_file in "$PROOF_HOME/"*.alethe ; do
  problem_file_name=`basename $proof_file ".alethe"`
  problem_file="$PROBLEM_HOME/""${problem_file_name%.*}"".smt2"

  #basename for problem and proof files
  new_problem_base="$RESULTS_HOME/$problem_file_name"
  new_proof_base="$RESULTS_HOME/$problem_file_name"
     
  #asserts can go over several lines :( So this is not possible
  #sed -i '/assert/d' $new_problem
  temp=$(<"$problem_file")
  #FIXME: Just give python script the file or only have python script for this whole workflow...
  newProblemContent="$(python3 Scripts/deleteAsserts.py "$temp" 2>&1)"

  onlyRewrites="$(sed '/all_simplify/!d' "$proof_file" 2>&1)"
  nr_rewrite=0

  if [ -z "$onlyRewrites" ]; then
    rm $new_problem
  else
    while IFS= read -r line
    do
     #built new proof and problem files
     new_problem=$new_problem_base"_$nr_rewrite.smt2"
     new_proof=$new_proof_base"_$nr_rewrite.alethe"
    
     #Write problem
     echo "$newProblemContent" > $new_problem
    
     #classify rewrite
     whichRewrite=$(echo "$line" | awk -F ':args' '{print $2}' | awk '{print $1}' )
     whichRewrite2="${whichRewrite:1}"

     if [ -z "$whichRewrite2" ]
     then
       echo "$problem_file_name""_""$nr_rewrite.smt2, none" >> $STATS
     else
       echo "$problem_file_name""_""$nr_rewrite.smt2, $whichRewrite2" >> $STATS
     fi

     #Write proof
     echo "unsat" > $new_proof
     echo "(assume a0 (false))" >> $new_proof
     echo $line | sed "s/step [^ ]* /step t0 /" >> $new_proof
     echo "(step t1 (cl (not false)) :rule false)" >> $new_proof
     echo "(step t2 (cl) :rule resolution :premises (a0 t1))" >> $new_proof
     nr_rewrite=$((nr_rewrite+1))
    done <<< "$onlyRewrites"
   fi
   
   if [[ $delete_files -eq 1 ]]
   then
     rm $problem_file #Delete original problem
   fi
done
fi
