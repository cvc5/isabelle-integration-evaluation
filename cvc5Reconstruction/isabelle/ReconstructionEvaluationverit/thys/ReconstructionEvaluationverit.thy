theory ReconstructionEvaluationverit
  imports "HOL-CVC.SMT_CVC"
begin

declare [[smt_verbose=false,smt_trace=false,smt_timeout=0.1,smt_reconstruction_step_timeout=0.1]]

declare [[smt_statistics_file="verit"]]



check_smt_dir "/home/lachnitt/Sources/isabelle-integration-evaluation/cvc5Reconstruction/data/benchmarks/verit/"

(*("problem", "eq_diamond16.smt2") (line 93 of "/home/lachnitt/Sources/isabelle-git/isabelle-emacs/src/HOL/CVC/ML/smt_check_external.ML")|
This is where it tiems out
check_smt_dir ("verit") "/home/lachnitt/Sources/isabelle-integration-evaluation/cvc5Reconstruction/Benchmark/Result/verit/"
end
*)

end
