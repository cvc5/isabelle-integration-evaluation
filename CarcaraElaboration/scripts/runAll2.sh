#!/bin/bash
source config

if [ $# -eq 0 ]; then
    echo "Usage: $0 <output directory>"
    exit 1
fi

rm -f "$BENCHMARK_HOME/"*;

echo "prepare isabelle"
$ISABELLE_BIN build -d $ISABELLE_HOME/src/HOL/ HOL-CVC ;

echo "Process benchmarks in batches of 50"

#Rename all .proof to .alethe
#Rename all .proof_elab to _elab.alethe
#Copy all .smt2 and make _elab.smt2
while read -r problem_file; do
  if [[ $problem_file != *_elaborated.smt2 ]] ;
  then
    file_without_extension="${problem_file%.*}"
    cp $problem_file $file_without_extension"_elaborated.smt2"
  fi;
done <<< $(find "$INPUT_BENCHMARK_HOME" -type f -name "*.smt2")

while read -r proof_file; do
  file_without_extension="${proof_file%.*}"
  file_without_extension="${file_without_extension%.*}"
  alethe_file=$file_without_extension".alethe"
  sed -i '1s/^/unsat\n/' $proof_file
  cp $proof_file $alethe_file
  rm $proof_file
done <<< $(find "$INPUT_BENCHMARK_HOME" -type f -name "*.smt2.proof")

while read -r proof_file; do
  file_without_extension="${proof_file%.*}"
  file_without_extension="${file_without_extension%.*}"
  echo $file_without_extension
  sed -i '1s/^/unsat\n/' $proof_file
  cp $proof_file $file_without_extension"_elaborated.alethe"
  rm $proof_file
done <<< $(find "$INPUT_BENCHMARK_HOME" -type f -name "*.smt2.proof_elab")


stats_name=$1
stats_dir=$RESULT_HOME/$stats_name
mkdir -p $stats_dir
    
while read -r problem_file; do
  if [[ $problem_file != *_elaborated.smt2 ]] ;
  then
   file_without_extension="${problem_file%.*}"
   echo "Processing $(basename $file_without_extension)"
   elab_file=$file_without_extension"_elaborated.smt2"
   file_with_alethe=$file_without_extension".alethe"
   elab_file_with_alethe=$file_without_extension"_elaborated.alethe"
   nr_elab_proof_lines=$(wc -l < $elab_file_with_alethe)
   if [ $nr_elab_proof_lines -le 70000 ] && [ $nr_elab_proof_lines -gt 40000 ];
   then
    cp $problem_file $BASE_DIR/Input2
    cp $elab_file $BASE_DIR/Input2
    cp $file_with_alethe $BASE_DIR/Input2
    cp $elab_file_with_alethe $BASE_DIR/Input2
     
    cp $problem_file $BENCHMARK_HOME
    cp $elab_file $BENCHMARK_HOME
    cp $file_with_alethe $BENCHMARK_HOME
    cp $elab_file_with_alethe $BENCHMARK_HOME
 
    current_time=$(date "+%Y.%m.%d-%H.%M.%S")
    curr_res_file=$stats_dir/$current_time".json"
    echo "Save results to $curr_res_file";

    # Run Isabelle on theory
    rm -f $ISABELLE_USER_HOME/"carcara"

    res=$(timeout 150s $ISABELLE_BIN build -c -d "$ISABELLE_BASE" "EvaluateReconstruction" 2>&1)
    error_code=$?
    echo $res
    #Copy result vom Isabelle run to Result directory
    cp $ISABELLE_USER_HOME/"carcara" $curr_res_file
    
    sed -i '1s/^/[\n/' $curr_res_file
    #Delete the last comma
    if [ $(wc -l < $curr_res_file) -gt 1 ]; then
      sed -i '$s/.$//' "$curr_res_file"
    fi

    sed -i -e '$a\'$'\n'']' $curr_res_file


    rm "$BENCHMARK_HOME/"*;
   else echo "elaborated proof too big: $file"
   fi;
  fi;
done <<< $(find "$INPUT_BENCHMARK_HOME" -type f -name "*.smt2")

python3 $SCRIPTS_HOME/combineChecker.py $stats_name

echo "Done with all benchmarks"
echo "Delete all files"
rm -f "$BENCHMARK_HOME/"*;

> $PROBLEM_LOG
