(*  Title:      HOL/SMT_Examples/SMT_Examples_CVC.thy
    Author:     Hanna Lachnitt, Stanford University
    Author:     Mathias Fleury, University of Freiburg


    rules in total
    rules with test
    without test
  
*)

theory CVC5_Rewrites
  imports HOL.SMT_CVC "../IsabelleCheckExternal/SMT_Check_External"
begin

declare[[rare_rec_mode=1]]
declare[[smt_trace=true,smt_verbose=true]]

declare[[smt_expert_debug_alethe_level=3]]
declare[[smt_expert_debug_alethe_files="all"]]

(*(define-rule or-not-refl ((t ?) (xs Bool :list)) (or (not (= t t)) xs) (or xs))*)
check_smt ("cvc5_proof")
  "./Benchmarks/CVC5_Rewrites/prob_00429_016041__12898890-t201.t7.t1.t1.smt2"
  "./Benchmarks/CVC5_Rewrites/prob_00429_016041__12898890-t201.t7.t1.t1.alethe"
