#!/bin/bash
out_name=$1
./scripts/collectOutput.sh output/benchmarks_baseline_cvc5_with_rewrite$out_name/out/ output/benchmarks_baseline_cvc5_with_rewrite$out_name/result/ cvc5_with_rewrite

python3 ./scripts/analyzeErrors3.py output/benchmarks_baseline_cvc5_with_rewrite$out_name/result/all_checking.json cvc5_with_rewrite
cp errors.txt saved_results/benchmarks_baseline$out_name/


cp output/benchmarks_baseline_cvc5_with_rewrite$out_name/result/all_checking.json saved_results/benchmarks_baseline$out_name/cvc5_with_rewrite_all_checking.json

sed -i 's/\/barrett\/scratch\/lachnitt\/non-incremental\/baseline_probs\/SMT2\///g' saved_results/benchmarks_baseline$out_name/cvc5_with_rewrite_all_checking.json
python3 ./scripts/analyzeErrors3.py saved_results/benchmarks_baseline$out_name/cvc5_with_rewrite_all_checking.json cvc5_with_rewrite


