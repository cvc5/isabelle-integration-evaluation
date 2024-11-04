#!/bin/bash
source config

if [ $# -eq 0 ]; then
    echo "Usage: $0 <output directory>"
    exit 1
fi

rm -f "$BENCHMARK_HOME/*";
#rm -f "$PREPROC_BENCHMARK_HOME/*";
#> $PROBLEM_LOG
echo "prepare isabelle"
$ISABELLE_BIN build -d $ISABELLE_HOME/src/HOL/ HOL-CVC ;

echo "Run preprocessing"
#$SCRIPTS_HOME/preproc.sh

echo "Process benchmarks in batches of 50"
rm -f "$BENCHMARK_HOME"/*;

while [ -s $PROBLEM_LOG ]; do
    lines=$(wc -l < $PROBLEM_LOG)
    echo "Benchmarks not tested yet: $lines"
    echo "Run veriT"
    $SCRIPTS_HOME/runVeriT.sh -r
    echo "Run Carcara"
    $SCRIPTS_HOME/runCarcara.sh
    echo "Run Isabelle"
    $SCRIPTS_HOME/runIsabelle.sh -f -d $1
    #if [ $? = 1 ]; then echo "runIsabelle script deleted benchmark, at some point re-run only non-run benchmarks here"; fi;
    rm -f "$BENCHMARK_HOME"/*;
done

echo "Done with all benchmarks"
echo "Delete all files"
rm -f "$BENCHMARK_HOME/*";
#rm -f "$PREPROC_BENCHMARK_HOME/*";
> $PROBLEM_LOG
