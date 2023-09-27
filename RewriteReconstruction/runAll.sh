#!/bin/bash

export USER_HOME=/barrett/scratch/lachnitt
ISABELLE_HOME=/barrett/scratch/lachnitt/Sources/isabelle-emacs/
AFP_HOME=/barrett/scratch/lachnitt/Sources/afp-2023-09-13/thys/Word_Lib
BASE_DIR=/barrett/scratch/lachnitt/Sources/isabelle-integration-evaluation/RewriteReconstruction


while [ ! -z "$(ls -A ./Benchmark)" ]
do

ISABELLE=$ISABELLE_HOME"bin/isabelle"
echo "init ..."

#Delete content of all results files
> ./Results/FileToRewrite.txt
> ./Results/ResultsWithoutRewrites.txt
> ./Results/ResultsWithRewrites.txt

BASE_DIR2="${BASE_DIR//\//\\\/}"
GEN_PROB=$BASE_DIR2"\/GeneratedProblems\/"
RESULTS_WITHOUT=$BASE_DIR2"\/Results\/ResultsWithoutRewrites.txt"
RESULTS_WITH=$BASE_DIR2"\/Results\/ResultsWithRewrites.txt"
echo $GEN_PROB

echo "get Alethe proofs ..."
./Scripts/runAlethe.sh 100 #Get proofs for 100 smt2 benchmarks at a time
echo "generate Benchmarks from Alethe proofs ..."
./Scripts/generateBenchmarks.sh 1 #Split up proofs into one problem and proof per rewrite, delete original problem

#Delete Alethe proofs
rm ./AletheProofs/*

#Consolidate results
#echo "file_name,timeWithoutLemmas" >> ./Results/ResultsWithoutRewrites.txt
#echo "file_name,timeWithLemmas" >> ./Results/ResultsWithRewrites.txt

#Run Isabelle for the first time
echo "run Isabelle with rewrite lemmas ..."
sed -i "98s/.*/(dsl_tac_initialize rewrite_name args ctxt t th)|/" $ISABELLE_HOME"src/HOL/CVC/ML/lethe_replay_all_simplify_methods.ML"
sed -i "45s/.*/check_smt_dir_stats \"${GEN_PROB}\" \"${RESULTS_WITH}\"/" ./thys/TestRewrites.thy
$ISABELLE build -d $AFP_HOME -d. EvaluateRewrites
sed -i '1s/^/file_name,timeWithLemmas\n/' ./Results/ResultsWithRewrites.txt

#Run Isabelle for the second time
echo "run Isabelle without rewrite lemmas ..."
sed -i "98s/.*/(try_auto_solo ctxt t)|/" $ISABELLE_HOME"src/HOL/CVC/ML/lethe_replay_all_simplify_methods.ML"
sed -i "45s/.*/check_smt_dir_stats \"$GEN_PROB\" \"${RESULTS_WITHOUT}\"/" ./thys/TestRewrites.thy
$ISABELLE build -d $AFP_HOME -d. EvaluateRewrites
sed -i '1s/^/file_name,timeWithoutLemmas\n/' ./Results/ResultsWithoutRewrites.txt

#Delete content of GeneratedProblems
rm ./GeneratedProblems/*

echo "connect all data ..."
python3 ./Scripts/connectStats.py
#Copy Results.csv to file with name of the current timestamp
#TODO: Write directly in here
current_time=$(date "+%Y.%m.%d-%H.%M.%S")
echo $current_time
res_file_name="res"$current_time".txt"
touch ./Results/Runs/$res_file_name
mv ./Results/Results.csv ./Results/Runs/$res_file_name
touch ./Results/Results.csv

echo "clean up ..."

#Delete content of all results files
> ./Results/FileToRewrite.txt
> ./Results/ResultsWithoutRewrites.txt
> ./Results/ResultsWithRewrites.txt

echo "done!"
done
exit
