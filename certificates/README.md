

#Preprocessing

Preprocessing a benchmark set <name> in <inputDir>:



The first three steps run locally and don't delete any benchmarks. They could be combined but even with large sets I had no performance problems so far and preferred the modularity.


1. Sometimes files end in .smt\_in, if so this script changes their extension to  .smt2

./preproc/renameExtension.sh <inputDir>

2. We don't support the tilde symbol. Sometimes it works to just omit them. 

./preproc/removeTilde.sh <inputDir> 

3. We don't support the (get-unsat-core) command. 

./preproc/removeGetUnsatCore <inputDir>



Now benchmarks are deleted:

4. Delete unsupported benchmarks with Slurm

./preproc/findUnsupWrapper.sh <input_dir>




TODO: This hardcodes the path to cvc5 right now... How do I change that.

