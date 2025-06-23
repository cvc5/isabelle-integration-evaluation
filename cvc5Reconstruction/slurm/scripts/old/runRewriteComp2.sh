#!/bin/bash


if [ $# -eq 0 ]; then
    echo "Usage: $0 <out_name>"
    exit 1
fi
out_dir=saved_results/benchmark_rewrite_cvc5_with_rewrite$out_name/

name="lemma"
output_dir=output/benchmarks_rewrite_$name"_cvc5_with_rewrite"$out_name/
./scripts/collectOutput.sh $output_dir/out/ $output_dir/result/ cvc5_with_rewrite
cp errors.txt $out_dir
cp $output_dir/result/all_checking.json $out_dir/$name"_all_checking.json" 




