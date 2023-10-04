#!/bin/bash

source config
line_nr_replace=123


nr_files=$(find "./Benchmark/" -maxdepth 1 -type f | wc -l)
nr_rewrites=0
nr_used=0
 
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

echo "get Alethe proofs ..."
./Scripts/runAlethe.sh 100 #Get proofs for 100 smt2 benchmarks at a time

nr_used=$(($nr_used + $(find "./AletheProofs/" -maxdepth 1 -type f | wc -l)))

echo "generate Benchmarks from Alethe proofs ..."
./Scripts/generateBenchmarks.sh 1 #Split up proofs into one problem and proof per rewrite, delete original problem
nr_curr_rewrites=$(find "./GeneratedProblems/" -maxdepth 1 -type f | wc -l)

if [ $nr_curr_rewrites -ne 0 ] #No rewrites in any proof
then 
nr_rewrites=$(($nr_rewrites + $nr_curr_rewrites))

#Delete Alethe proofs
rm -f ./AletheProofs/*

#Run Isabelle for the first time
echo "run Isabelle with rewrite lemmas ..."
sed -i "${line_nr_replace}s/.*/(dsl_tac_initialize rewrite_name args ctxt t th)|/" $ISABELLE_HOME"src/HOL/CVC/ML/lethe_replay_all_simplify_methods.ML"
sed -i "45s/.*/check_smt_dir_stats \"${GEN_PROB}\" \"${RESULTS_WITH}\"/" ./thys/TestRewrites.thy
$ISABELLE build -d $AFP_HOME -d. EvaluateRewrites
sed -i '1s/^/file_name,timeWithLemmas\n/' ./Results/ResultsWithRewrites.txt

#Run Isabelle for the second time
echo "run Isabelle without rewrite lemmas ..."
sed -i "${line_nr_replace}s/.*/(try_auto_solo ctxt t)|/" $ISABELLE_HOME"src/HOL/CVC/ML/lethe_replay_all_simplify_methods.ML"
sed -i "45s/.*/check_smt_dir_stats \"$GEN_PROB\" \"${RESULTS_WITHOUT}\"/" ./thys/TestRewrites.thy
$ISABELLE build -d $AFP_HOME -d. EvaluateRewrites
sed -i '1s/^/file_name,timeWithoutLemmas\n/' ./Results/ResultsWithoutRewrites.txt

#Delete content of GeneratedProblems
#rm -f ./GeneratedProblems/*

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
#> ./Results/FileToRewrite.txt
#> ./Results/ResultsWithoutRewrites.txt
#> ./Results/ResultsWithRewrites.txt

echo "done!"
else
 rm -f ./Benchmark/*
fi
done

sed -i "${line_nr_replace}s/.*/(dsl_tac_initialize rewrite_name args ctxt t th)|/" $ISABELLE_HOME"src/HOL/CVC/ML/lethe_replay_all_simplify_methods.ML"

echo "------------------------------------------------"
echo "------------------------------------------------"
echo "------------------------------------------------"
echo "Number of SMT-LIB problems found: $nr_files"
echo "Of these $nr_used could be used (e.g., timeouts)"
echo "Checked a total of $nr_rewrites rewrites"

exit
