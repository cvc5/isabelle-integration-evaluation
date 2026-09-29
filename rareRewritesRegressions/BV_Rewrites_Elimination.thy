(*  Title:      HOL/SMT_Examples/SMT_Examples_CVC.thy
    Author:     Hanna Lachnitt, Stanford University
    Author:     Mathias Fleury, University of Freiburg
*)

theory BV_Rewrites_Elimination
  imports HOL.SMT_CVC "HOL-Library.SMT_CVC_Word" "SMT_Check_External"
begin

declare[[smt_trace=true,smt_verbose=true]]

declare[[smt_expert_debug_alethe_level=3]]
declare[[smt_expert_debug_alethe_files="alethe_replay_rare"]]
declare[[rare_rec_mode=1]]

(*bv-ugt-eliminate*)
check_smt ("cvc5_proof")
  "./Benchmarks/BV_Rewrites_Elimination/bv-ugt-eliminate.smt2"
  "./Benchmarks/BV_Rewrites_Elimination/bv-ugt-eliminate.alethe"

(*bv-uge-eliminate*)
check_smt ("cvc5_proof")
  "./Benchmarks/BV_Rewrites_Elimination/bv-uge-eliminate.smt2"
  "./Benchmarks/BV_Rewrites_Elimination/bv-uge-eliminate.alethe"

(*bv-sgt-eliminate*)
check_smt ("cvc5_proof")
  "./Benchmarks/BV_Rewrites_Elimination/bv-sgt-eliminate.smt2"
  "./Benchmarks/BV_Rewrites_Elimination/bv-sgt-eliminate.alethe"

(*bv-sge-eliminate*)

(*bv-sle-eliminate*)
check_smt ("cvc5_proof")
  "./Benchmarks/BV_Rewrites_Elimination/bv-sle-eliminate.smt2"
  "./Benchmarks/BV_Rewrites_Elimination/bv-sle-eliminate.alethe"

(*bv-redor-eliminate*)

(*bv-redand-eliminate*)

(*bv-ule-eliminate*)
check_smt ("cvc5_proof")
  "./Benchmarks/BV_Rewrites_Elimination/bv-ule-eliminate.smt2"
  "./Benchmarks/BV_Rewrites_Elimination/bv-ule-eliminate.alethe"

(*bv-comp-eliminate*)
check_smt ("cvc5_proof")
  "./Benchmarks/BV_Rewrites_Elimination/bv-comp-eliminate.smt2"
  "./Benchmarks/BV_Rewrites_Elimination/bv-comp-eliminate.alethe"

(*bv-rotate-left-eliminate-1*)
check_smt ("cvc5_proof")
  "./Benchmarks/BV_Rewrites_Elimination/bv-rotate-left-eliminate-1.smt2"
  "./Benchmarks/BV_Rewrites_Elimination/bv-rotate-left-eliminate-1.alethe"

(*bv-rotate-left-eliminate-2*)
check_smt ("cvc5_proof")
  "./Benchmarks/BV_Rewrites_Elimination/bv-rotate-left-eliminate-2.smt2"
  "./Benchmarks/BV_Rewrites_Elimination/bv-rotate-left-eliminate-2.alethe"

(*bv-rotate-right-eliminate-1*)
check_smt ("cvc5_proof")
  "./Benchmarks/BV_Rewrites_Elimination/bv-rotate-right-eliminate-1.smt2"
  "./Benchmarks/BV_Rewrites_Elimination/bv-rotate-right-eliminate-1.alethe"

(*bv-rotate-right-eliminate-2*)
check_smt ("cvc5_proof")
  "./Benchmarks/BV_Rewrites_Elimination/bv-rotate-right-eliminate-2.smt2"
  "./Benchmarks/BV_Rewrites_Elimination/bv-rotate-right-eliminate-2.alethe"

(*bv-nand-eliminate*)
check_smt ("cvc5_proof")
  "./Benchmarks/BV_Rewrites_Elimination/bv-nand-eliminate.smt2"
  "./Benchmarks/BV_Rewrites_Elimination/bv-nand-eliminate.alethe"

(*bv-nor-eliminate*)
check_smt ("cvc5_proof")
  "./Benchmarks/BV_Rewrites_Elimination/bv-nor-eliminate.smt2"
  "./Benchmarks/BV_Rewrites_Elimination/bv-nor-eliminate.alethe"

(*bv-xnor-eliminate*)
check_smt ("cvc5_proof")
  "./Benchmarks/BV_Rewrites_Elimination/bv-xnor-eliminate.smt2"
  "./Benchmarks/BV_Rewrites_Elimination/bv-xnor-eliminate.alethe"

(*bv-sdiv-eliminate*)
check_smt ("cvc5_proof")
  "./Benchmarks/BV_Rewrites_Elimination/bv-sdiv-eliminate.smt2"
  "./Benchmarks/BV_Rewrites_Elimination/bv-sdiv-eliminate.alethe"

(*bv-zero-extend-eliminate*)

(*bv-uaddo-eliminate*)

(*bv-saddo-eliminate*)

(*bv-sdivo-eliminate*)

(*bv-smod-eliminate*)
check_smt ("cvc5_proof")
  "./Benchmarks/BV_Rewrites_Elimination/bv-smod-eliminate.smt2"
  "./Benchmarks/BV_Rewrites_Elimination/bv-smod-eliminate.alethe"

(*bv-srem-eliminate*)
check_smt ("cvc5_proof")
  "./Benchmarks/BV_Rewrites_Elimination/bv-srem-eliminate.smt2"
  "./Benchmarks/BV_Rewrites_Elimination/bv-srem-eliminate.alethe"

(*bv-usubo-eliminate*)

(*bv-ssubo-eliminate*)

(*bv-nego-eliminate*)


end
