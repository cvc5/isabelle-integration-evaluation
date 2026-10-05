#!/usr/bin/env bash
trap "cd \"${PWD}\"" EXIT

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR/..

echo "Bool rules"
./scripts/check_rules_list.sh -q Benchmarks/Bool_Rewrites/bool-rules-list.txt 

echo -e "\nBuiltin rules"
./scripts/check_rules_list.sh -q Benchmarks/Builtin_Rewrites/builtin-rules-list.txt 
./scripts/check_rules_list.sh -q Benchmarks/UF_BV_Rewrites/uf-bv-rules-list.txt

echo -e "\nArith rules"
./scripts/check_rules_list.sh -q Benchmarks/Arith_Rewrites/arith-rules-list.txt

echo -e "\nUF rules"
./scripts/check_rules_list.sh -q Benchmarks/UF_Rewrites/uf-rules-list.txt

echo -e "\nBV rules"
./scripts/check_rules_list.sh -q Benchmarks/BV_Rewrites/bv-rules-list.txt
./scripts/check_rules_list.sh -q Benchmarks/BV_Rewrites_Elimination/bv-elimination-rules-list.txt 
./scripts/check_rules_list.sh -q Benchmarks/BV_Rewrites_Simplification/bv-simplification-rules-list.txt 

