theory Classification
  imports Main
begin


named_theorems rare_rewrites_simple \<open>RARE rewrites that don't contain lists or are star rules \<close>
named_theorems rare_rewrites_complex \<open>RARE rewrites that contain lists or are star rules \<close>
named_theorems rare_rewrites_all \<open>All RARE rewrites\<close>



named_theorems rare_arith_rewrites_simple \<open>Arithmetic RARE rewrites that don't contain lists or are star rules \<close>
named_theorems rare_arith_rewrites_complex \<open>Arithmetic RARE rewrites that contain lists or are star rules \<close>
named_theorems rare_arith_rewrites_all \<open>Arithmetic RARE rewrites\<close>





lemmas [rare_arith_rewrites_simple] =
"Alethe_Arith_Rewrites.rewrite_arith_elim_gt"
"Alethe_Arith_Rewrites.rewrite_arith_elim_lt"
"Alethe_Arith_Rewrites.rewrite_arith_elim_int_gt"
"Alethe_Arith_Rewrites.rewrite_arith_elim_int_lt"
"Alethe_Arith_Rewrites.rewrite_arith_elim_leq"
"Alethe_Arith_Rewrites.rewrite_arith_leq_norm"
"Alethe_Arith_Rewrites.rewrite_arith_geq_tighten"
"Alethe_Arith_Rewrites.rewrite_arith_geq_norm1_int"
"Alethe_Arith_Rewrites.rewrite_arith_divisible_elim"
"Alethe_Arith_Rewrites.rewrite_arith_geq_ite_lift"
"Alethe_Arith_Rewrites.rewrite_arith_geq_ite_lift"
"Alethe_Arith_Rewrites.rewrite_arith_leq_ite_lift"
"Alethe_Arith_Rewrites.rewrite_arith_min_lt1"
"Alethe_Arith_Rewrites.rewrite_arith_min_lt2"
"Alethe_Arith_Rewrites.rewrite_arith_max_geq1"
"Alethe_Arith_Rewrites.rewrite_arith_max_geq2"

lemmas [rare_arith_rewrites_complex] =
"Alethe_Arith_Rewrites.rewrite_arith_eq_elim_int"

lemmas [rare_arith_rewrites_all] = rare_arith_rewrites_simple rare_arith_rewrites_complex


named_theorems rare_bool_rewrites_simple \<open>Boolean RARE rewrites that don't contain lists or are star rules \<close>
named_theorems rare_bool_rewrites_complex \<open>Boolean RARE rewrites that contain lists or are star rules \<close>
named_theorems rare_bool_rewrites_all \<open>Boolean RARE rewrites\<close>


lemmas [rare_bool_rewrites_simple] =
"Alethe_Boolean_Rewrites.rewrite_bool_double_not_elim"
"Alethe_Boolean_Rewrites.rewrite_bool_not_true"
"Alethe_Boolean_Rewrites.rewrite_bool_not_false"
"Alethe_Boolean_Rewrites.rewrite_bool_eq_true"
"Alethe_Boolean_Rewrites.rewrite_bool_eq_false"
"Alethe_Boolean_Rewrites.rewrite_bool_eq_nrefl"
"Alethe_Boolean_Rewrites.rewrite_bool_impl_false1"
"Alethe_Boolean_Rewrites.rewrite_bool_impl_false2"
"Alethe_Boolean_Rewrites.rewrite_bool_impl_true1"
"Alethe_Boolean_Rewrites.rewrite_bool_impl_true2"
"Alethe_Boolean_Rewrites.rewrite_bool_impl_elim"
"Alethe_Boolean_Rewrites.rewrite_bool_dual_impl_eq"
"Alethe_Boolean_Rewrites.rewrite_bool_implies_de_morgan"
"Alethe_Boolean_Rewrites.rewrite_bool_xor_refl"
"Alethe_Boolean_Rewrites.rewrite_bool_xor_nrefl"
"Alethe_Boolean_Rewrites.rewrite_bool_xor_false"
"Alethe_Boolean_Rewrites.rewrite_bool_xor_true"
"Alethe_Boolean_Rewrites.rewrite_bool_xor_comm"
"Alethe_Boolean_Rewrites.rewrite_bool_xor_elim"
"Alethe_Boolean_Rewrites.rewrite_bool_not_xor_elim"
"Alethe_Boolean_Rewrites.rewrite_bool_not_eq_elim1"
"Alethe_Boolean_Rewrites.rewrite_bool_not_eq_elim2"
"Alethe_Boolean_Rewrites.rewrite_ite_neg_branch"
"Alethe_Boolean_Rewrites.rewrite_ite_then_true"
"Alethe_Boolean_Rewrites.rewrite_ite_else_false"
"Alethe_Boolean_Rewrites.rewrite_ite_then_false"
"Alethe_Boolean_Rewrites.rewrite_ite_else_true"
"Alethe_Boolean_Rewrites.rewrite_ite_then_lookahead_self"
"Alethe_Boolean_Rewrites.rewrite_ite_else_lookahead_self"
"Alethe_Boolean_Rewrites.rewrite_ite_then_lookahead_not_self"
"Alethe_Boolean_Rewrites.rewrite_ite_else_lookahead_not_self"
"Alethe_Boolean_Rewrites.rewrite_ite_expand"
"Alethe_Boolean_Rewrites.rewrite_bool_not_ite_elim"
"Alethe_Builtin_Rewrites.rewrite_ite_true_cond"
"Alethe_Builtin_Rewrites.rewrite_ite_false_cond"
"Alethe_Builtin_Rewrites.rewrite_ite_not_cond"
"Alethe_Builtin_Rewrites.rewrite_ite_eq_branch"
"Alethe_Builtin_Rewrites.rewrite_ite_then_lookahead"
"Alethe_Builtin_Rewrites.rewrite_ite_else_lookahead"
"Alethe_Builtin_Rewrites.rewrite_ite_then_neg_lookahead"
"Alethe_Builtin_Rewrites.rewrite_ite_else_neg_lookahead"

lemmas [rare_bool_rewrites_complex] =
"Alethe_Boolean_Rewrites.rewrite_bool_and_conf"
"Alethe_Boolean_Rewrites.rewrite_bool_and_conf2"
"Alethe_Boolean_Rewrites.rewrite_bool_or_taut"
"Alethe_Boolean_Rewrites.rewrite_bool_or_taut2"
"Alethe_Boolean_Rewrites.rewrite_bool_or_de_morgan"
"Alethe_Boolean_Rewrites.rewrite_bool_and_de_morgan"
"Alethe_Boolean_Rewrites.rewrite_bool_or_and_distrib"
"Alethe_Boolean_Rewrites.rewrite_bool_implies_or_distrib"

lemmas [rare_bool_rewrites_all] = rare_bool_rewrites_simple rare_bool_rewrites_complex


named_theorems rare_UF_Rewrites_simple \<open>Uninterpreted Functions rewrites that don't contain lists or are star rules \<close>
named_theorems rare_UF_Rewrites_complex \<open>Uninterpreted Functions that contain lists or are star rules \<close>
named_theorems rare_UF_Rewrites_all \<open>Uninterpreted Functions rewrites\<close>

lemmas [rare_UF_Rewrites_simple] =
"Alethe_UF_Rewrites.rewrite_eq_refl"
"Alethe_UF_Rewrites.rewrite_eq_symm"
"Alethe_UF_Rewrites.rewrite_eq_cond_deq"
"Alethe_UF_Rewrites.rewrite_eq_ite_lift"
"Alethe_UF_Rewrites.rewrite_distinct_binary_elim"
lemmas [rare_UF_Rewrites_all] = rare_UF_Rewrites_simple

named_theorems rare_cvc5_Rewrites_simple \<open>Rewrites only produced by the cvc5 Alethe translation that don't contain lists or are star rules \<close>
named_theorems rare_cvc5_Rewrites_complex \<open>Rewrites only produced by the cvc5 Alethe translation that contain lists or are star rules \<close>
named_theorems rare_cvc5_Rewrites_all \<open>Rewrites only produced by the cvc5 Alethe translation rewrites\<close>


lemmas [rare_cvc5_Rewrites_simple] =
"Alethe_cvc5_Rewrites.rewrite_ite_eq"
 "Alethe_cvc5_Rewrites.rewrite_distinct_binary_elim"
lemmas [rare_cvc5_Rewrites_complex] =
"Alethe_cvc5_Rewrites.rewrite_or_not_refl"
lemmas [rare_cvc5_Rewrites_all] = rare_cvc5_Rewrites_simple rare_cvc5_Rewrites_complex

(*All*)

lemmas [rare_rewrites_simple] = rare_bool_rewrites_simple rare_arith_rewrites_simple rare_UF_Rewrites_simple rare_cvc5_Rewrites_simple
lemmas [rare_rewrites_complex] = rare_bool_rewrites_complex rare_arith_rewrites_complex rare_UF_Rewrites_complex rare_cvc5_Rewrites_complex
lemmas [rare_rewrites_all] = rare_rewrites_simple rare_rewrites_complex










lemmas [rare_arith_rewrites_simple] =
"Alethe_Arith_Real_Rewrites.rewrite_arith_geq_norm1_real"
"Alethe_Arith_Real_Rewrites.rewrite_arith_eq_elim_real"
"Alethe_Arith_Real_Rewrites.rewrite_arith_to_int_to_real"
"Alethe_Arith_Real_Rewrites.rewrite_arith_int_eq_conflict"
"Alethe_Arith_Real_Rewrites.rewrite_arith_int_geq_tighten"

lemmas [rare_rewrites_simple] = rare_arith_rewrites_simple
lemmas [rare_rewrites_all] = rare_arith_rewrites_simple


end