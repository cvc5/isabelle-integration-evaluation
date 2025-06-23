#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <out_name>"
    exit 1
fi

out_name=$1
SCRIPT_DIR=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/scripts/

cd /barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/
mkdir saved_results/benchmarks_metrics$out_name

set_name="QF_UF"
base_dir_path=/barrett/scratch/lachnitt/non-incremental/sample_sets/"$set_name"_sample_mod/proofs/
config="cvc5_with_rewrite"
$SCRIPT_DIR/runSet.sh "$base_dir_path/list_viable_"$config".txt" "$base_dir_path/"$set_name"_sample_"$config"/" "$config" $out_name$set_name
config="verit"
$SCRIPT_DIR/runSet.sh "$base_dir_path/list_viable_"$config".txt" "$base_dir_path/"$set_name"_sample_"$config"/" "$config" $out_name$set_name

set_name="QF_LIA"
base_dir_path=/barrett/scratch/lachnitt/non-incremental/sample_sets/"$set_name"_sample_mod/proofs/
config="cvc5_with_rewrite"
$SCRIPT_DIR/runSet.sh "$base_dir_path/list_viable_"$config".txt" "$base_dir_path/"$set_name"_sample_"$config"/" "$config" $out_name$set_name
config="verit"
$SCRIPT_DIR/runSet.sh "$base_dir_path/list_viable_"$config".txt" "$base_dir_path/"$set_name"_sample_"$config"/" "$config" $out_name$set_name


set_name="QF_LRA"
base_dir_path=/barrett/scratch/lachnitt/non-incremental/sample_sets/"$set_name"_sample_mod/proofs/
config="cvc5_with_rewrite"
$SCRIPT_DIR/runSet.sh "$base_dir_path/list_viable_"$config".txt" "$base_dir_path/"$set_name"_sample_"$config"/" "$config" $out_name$set_name
config="verit"
$SCRIPT_DIR/runSet.sh "$base_dir_path/list_viable_"$config".txt" "$base_dir_path/"$set_name"_sample_"$config"/" "$config" $out_name$set_name


set_name="UF"
base_dir_path=/barrett/scratch/lachnitt/non-incremental/sample_sets/"$set_name"_sample_mod/proofs/
config="cvc5_with_rewrite"
$SCRIPT_DIR/runSet.sh "$base_dir_path/list_viable_"$config".txt" "$base_dir_path/"$set_name"_sample_"$config"/" "$config" $out_name$set_name
config="verit"
$SCRIPT_DIR/runSet.sh "$base_dir_path/list_viable_"$config".txt" "$base_dir_path/"$set_name"_sample_"$config"/" "$config" $out_name$set_name


