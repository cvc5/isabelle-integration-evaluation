#!/bin/bash


INPUT_DIR=$1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"


echo "------------------------------"

echo "Renaming any .smt_in files to .smt2"
$SCRIPT_DIR/renameExtension.sh $INPUT_DIR

echo "Removing any ~ in problem"
$SCRIPT_DIR/removeTilde.sh $INPUT_DIR

echo "Deleting (get-unsat-core) commands"
$SCRIPT_DIR/removeGetUnsatCore.sh $INPUT_DIR

echo "------------------------------"

nr_bench=$(find . -type f -name "*.smt2" | wc -l)
echo "Found $nr_bench benchmarks"


