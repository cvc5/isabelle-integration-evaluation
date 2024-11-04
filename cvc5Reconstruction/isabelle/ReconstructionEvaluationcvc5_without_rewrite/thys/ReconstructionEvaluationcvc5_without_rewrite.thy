theory ReconstructionEvaluationcvc5_without_rewrite
  imports "HOL-CVC.SMT_CVC" "HOL.Real"
begin

declare [[smt_oracle]]
declare [[smt_statistics_file="cvc5_without_rewrite"]]
declare [[smt_verbose=false,smt_trace=false,smt_debug_verit=false,smt_timeout=10.0,smt_reconstruction_step_timeout=5.0]]
declare[[smt_rec_evaluation]]
declare[[smt_alethe_no_assumption=true]]
check_smt_dir ("cvc5_proof") "/home/lachnitt/Sources/isabelle-integration-evaluation/cvc5Reconstruction/data/benchmarks/cvc5_without_rewrite/"
end
