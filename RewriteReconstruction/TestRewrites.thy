theory TestRewrites
  imports "HOL-CVC.SMT_CVC"
  keywords "check_smt_dir_stats" :: diag

begin

(*This file is outside of the repo since it is only used for our research*)

(*Plan: 
Execute check_smt_dir but write output in file.
Each input file only has one rewrite step in it
  - Have two all_simplify methods that switch with a flag: One that only simps and the other that uses lemmas (TODO)
  - If one proof fails don't stop the whole checking process
  - Write down times that it took for reconstruction or -1 when proof failed. 
Execute with command line on cluster


\<Rightarrow> Switching live between the two methods seems complicated. Better do one after the other.
Put the modified one in different branch

\<Rightarrow> We record the whole time (generating the problem and reconstructing). This does not matter for now since 
we are only interested in comparing the two methods.
*)


ML \<open>

(*Call replay from SMT_Solver and add replay_data on your own*)
(*The problem (name.smt2) and proof files (name.alethe) should be in the same directory.*)
val _ = Outer_Syntax.local_theory \<^command_keyword>\<open>check_smt_dir_stats\<close>
         "parse a directory with SMTLIB2 format and check proof. <dir>"
   (Scan.optional (\<^keyword>\<open>(\<close> |-- Parse.string --| \<^keyword>\<open>)\<close>) "cvc5" --
    (Parse.string -- Parse.string)
    >> (fn (prover, (dir_name,output_file)) => fn lthy =>
  let
    val _ = SMT_Check_External.test_all_benchmarks prover dir_name (SOME output_file) lthy
  in                             
   lthy
   end))

\<close>



check_smt_dir_stats "~/Sources/IsabelleEvaluation/GeneratedProblems/" "~/Sources/IsabelleEvaluation/Results/ResultsWithoutRewrites.txt"




end