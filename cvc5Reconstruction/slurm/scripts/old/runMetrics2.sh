#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <out_name>"
    exit 1
fi

out_name=$1
SCRIPT_HOME=/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/scripts/
res_dir=saved_results/benchmarks_metrics$out_name
mkdir -p $res_dir
cd /barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm

logic_name=QF_UF
config=cvc5_with_rewrite
out_dir=output/benchmarks_"$config"$out_name$logic_name
$SCRIPT_HOME/runSetSlurmWrapperEvaluate.sh $out_dir/out/ $out_dir/result/out.json $config
python3 $SCRIPT_HOME/analyzeErrors3.py $out_dir/result/out.json $config
cp errors.txt $res_dir/"$config"_$logic_name"_errors.txt"
cp $out_dir/result/out.json $res_dir/"$config"_"$logic_name"_all_checking.json
config=verit
out_dir=output/benchmarks_"$config"$out_name$logic_name
$SCRIPT_HOME/runSetSlurmWrapperEvaluate.sh $out_dir/out/ $out_dir/result/out.json $config
python3 $SCRIPT_HOME/analyzeErrors3.py $out_dir/result/out.json $config
cp errors.txt $res_dir/"$config"_$logic_name"_errors.txt"
cp $out_dir/result/out.json $res_dir/"$config"_"$logic_name"_all_checking.json
python3 $SCRIPT_HOME/combineCheckerOutput.py $res_dir/cvc5_with_rewrite_"$logic_name"_all_checking.json $res_dir/verit_"$logic_name"_all_checking.json $res_dir/"$logic_name"_all_checking.json


logic_name=QF_LIA
config=cvc5_with_rewrite
out_dir=output/benchmarks_"$config"$out_name$logic_name
$SCRIPT_HOME/runSetSlurmWrapperEvaluate.sh $out_dir/out/ $out_dir/result/out.json $config
python3 $SCRIPT_HOME/analyzeErrors3.py $out_dir/result/out.json cvc5_with_rewrite
cp errors.txt $res_dir/"$config"_$logic_name"_errors.txt"
cp $out_dir/result/out.json $res_dir/"$config"_"$logic_name"_all_checking.json
config=verit
out_dir=output/benchmarks_"$config"$out_name$logic_name
$SCRIPT_HOME/runSetSlurmWrapperEvaluate.sh $out_dir/out/ $out_dir/result/out.json $config
python3 $SCRIPT_HOME/analyzeErrors3.py $out_dir/result/out.json cvc5_with_rewrite
cp errors.txt $res_dir/"$config"_$logic_name"_errors.txt"
cp $out_dir/result/out.json $res_dir/"$config"_"$logic_name"_all_checking.json
python3 $SCRIPT_HOME/combineCheckerOutput.py $res_dir/cvc5_with_rewrite_"$logic_name"_all_checking.json $res_dir/verit_"$logic_name"_all_checking.json $res_dir/"$logic_name"_all_checking.json

logic_name=QF_LRA
config=cvc5_with_rewrite
out_dir=output/benchmarks_"$config"$out_name$logic_name
$SCRIPT_HOME/runSetSlurmWrapperEvaluate.sh $out_dir/out/ $out_dir/result/out.json $config
python3 $SCRIPT_HOME/analyzeErrors3.py $out_dir/result/out.json $config
cp errors.txt $res_dir/"$config"_$logic_name"_errors.txt"
cp $out_dir/result/out.json $res_dir/"$config"_"$logic_name"_all_checking.json
config=verit
out_dir=output/benchmarks_"$config"$out_name$logic_name
$SCRIPT_HOME/runSetSlurmWrapperEvaluate.sh $out_dir/out/ $out_dir/result/out.json $config
python3 $SCRIPT_HOME/analyzeErrors3.py $out_dir/result/out.json $config
cp errors.txt $res_dir/"$config"_$logic_name"_errors.txt"
cp $out_dir/result/out.json $res_dir/"$config"_"$logic_name"_all_checking.json
python3 $SCRIPT_HOME/combineCheckerOutput.py $res_dir/cvc5_with_rewrite_"$logic_name"_all_checking.json $res_dir/verit_"$logic_name"_all_checking.json $res_dir/"$logic_name"_all_checking.json


logic_name=UF
config=cvc5_with_rewrite
out_dir=output/benchmarks_"$config"$out_name$logic_name
$SCRIPT_HOME/runSetSlurmWrapperEvaluate.sh $out_dir/out/ $out_dir/result/out.json $config
python3 $SCRIPT_HOME/analyzeErrors3.py $out_dir/result/out.json $config
cp errors.txt $res_dir/"$config"_$logic_name"_errors.txt"
cp $out_dir/result/out.json $res_dir/"$config"_"$logic_name"_all_checking.json
config=verit
out_dir=output/benchmarks_"$config"$out_name$logic_name
$SCRIPT_HOME/runSetSlurmWrapperEvaluate.sh $out_dir/out/ $out_dir/result/out.json $config
python3 $SCRIPT_HOME/analyzeErrors3.py $out_dir/result/out.json $config
cp errors.txt $res_dir/"$config"_$logic_name"_errors.txt"
cp $out_dir/result/out.json $res_dir/"$config"_"$logic_name"_all_checking.json
python3 $SCRIPT_HOME/combineCheckerOutput.py $res_dir/cvc5_with_rewrite_"$logic_name"_all_checking.json $res_dir/verit_"$logic_name"_all_checking.json $res_dir/"$logic_name"_all_checking.json





