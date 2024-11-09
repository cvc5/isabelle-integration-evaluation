theory test
  imports "HOL-CVC.SMT_CVC" "HOL.Real"
begin

declare [[smt_oracle]]
declare [[smt_statistics_file="test"]]
declare [[smt_verbose=false,smt_trace=false,smt_debug_verit=false,smt_timeout=10.0,smt_reconstruction_step_timeout=5.0]]
declare[[smt_rec_evaluation]]
declare[[smt_alethe_no_assumption=true]]




check_smt ("cvc5_proof") "/home/lachnitt/Sources/isabelle-integration-evaluation/cvc5Reconstruction/benchmark_precompiled/QF_UF_small_cvc5/2018-Goel-hwbench/QF_UF_counter_v_ab_reg_max.smt2"
"/home/lachnitt/Sources/isabelle-integration-evaluation/cvc5Reconstruction/benchmark_precompiled/QF_UF_small_cvc5/2018-Goel-hwbench/QF_UF_counter_v_ab_reg_max.alethe"


end

