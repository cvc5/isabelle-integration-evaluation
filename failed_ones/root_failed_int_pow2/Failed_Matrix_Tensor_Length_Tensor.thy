(*  Title:      root_failed_int_pow2/Failed_Matrix_Tensor_Length_Tensor.thy *)

section \<open>Isolated length_Tensor\<close>

theory Failed_Matrix_Tensor_Length_Tensor
imports Matrix.Utility Matrix.Matrix_Legacy
begin

locale mult =
 fixes id::"'a"
 fixes f::" 'a \<Rightarrow> 'a \<Rightarrow> 'a " (infixl \<open>*\<close> 60)
 assumes comm:" f a  b = f b  a "
 assumes assoc:" (f (f a b) c) = (f a (f b c))"
 assumes left_id:" f id x = x"
 assumes right_id:"f x id = x"

context mult
begin

primrec times:: "'a \<Rightarrow> 'a vec \<Rightarrow> 'a vec"
where
"times n [] = []"|
"times n (y#ys) = (f n y)#(times n ys)"

lemma preserving_length: "length (times n y) = (length y)"
 by(induction y)(auto)

primrec vec_vec_Tensor:: "'a vec \<Rightarrow> 'a vec \<Rightarrow> 'a vec"
where
"vec_vec_Tensor [] ys = []"|
"vec_vec_Tensor (x#xs) ys = (times x ys)@(vec_vec_Tensor xs ys)"

theorem vec_vec_Tensor_length :
 "(length(vec_vec_Tensor x y)) = (length x)*(length y)"
 by(induction x)(auto simp add: preserving_length)

primrec vec_mat_Tensor::"'a vec \<Rightarrow> 'a mat \<Rightarrow>'a mat"
where
"vec_mat_Tensor xs []  = []"|
"vec_mat_Tensor xs (ys#yss) = (vec_vec_Tensor xs ys)#(vec_mat_Tensor xs yss)"

theorem vec_mat_Tensor_length:
 "length(vec_mat_Tensor xs ys) = length ys"
 by(induction ys)(auto)

primrec Tensor::" 'a mat \<Rightarrow> 'a mat \<Rightarrow>'a mat" (infixl \<open>\<otimes>\<close> 63)
where
"Tensor [] xs = []"|
"Tensor (x#xs) ys = (vec_mat_Tensor x ys)@(Tensor xs ys)"

lemma length_Tensor:" (length (M1\<otimes>M2)) = (length M1)*(length M2)"
proof(induct M1)
 case Nil
  show ?case by auto
 next
 case (Cons a M1)
  have "((a # M1) \<otimes> M2) = (vec_mat_Tensor a M2)@(M1 \<otimes> M2)"
               using Tensor.simps(2) by auto
  then have 1:
          "length ((a # M1) \<otimes> M2) = length ((vec_mat_Tensor a M2)@(M1 \<otimes> M2))"
               by auto
  have 2:"length ((vec_mat_Tensor a M2)@(M1 \<otimes> M2))
              = length (vec_mat_Tensor a M2)+ length (M1 \<otimes> M2)"
               using append_def
               by auto
  have 3:"(length (vec_mat_Tensor a M2)) = length M2"
               using vec_mat_Tensor_length by (auto)
  have 4:"length (M1 \<otimes> M2) = (length M1)*(length M2)"
               using  Cons.hyps by auto
  with 2 3 have "length ((vec_mat_Tensor a M2)@(M1 \<otimes> M2))
                              = (length M2) + (length M1)*(length M2)"
               by auto
  then have 5:
    "length ((vec_mat_Tensor a M2)@(M1 \<otimes> M2)) = (1 + (length M1))*(length M2)"
               by auto
  with 1  have "length ((a # M1) \<otimes> M2) = ((length (a # M1)) * (length M2))"
          by auto
  then show ?case by auto
qed

end

end
