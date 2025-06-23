#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <out_name>"
    exit 1
fi

out_name=$1
save_dir=saved_results/benchmarks_rewrite_cvc5_with_rewrite$out_name/

mkdir -p $save_dir


./scripts/runSet.sh /barrett/scratch/lachnitt/non-incremental/slice/QF_UF_sample_rare_slices_all_solving.txt cvc5_with_rewrite /barrett/scratch/lachnitt/non-incremental/slice/QF_UF_sample_rare_slices/ rewrite_simp $out_name "1"
./scripts/runSet.sh /barrett/scratch/lachnitt/non-incremental/slice/QF_UF_sample_rare_slices_all_solving.txt cvc5_with_rewrite /barrett/scratch/lachnitt/non-incremental/slice/QF_UF_sample_rare_slices/ rewrite_lemma $out_name "0"

