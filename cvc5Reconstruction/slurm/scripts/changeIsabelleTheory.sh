#!/bin/bash

input_problem_file=$1
input_proof_file=$2


sed -i "15s/.*/$input_problem_file/" /barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/test.thy


sed -i "16s/.*/$input_proof_file/" /barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/cvc5Reconstruction/slurm/test.thy
