(*  Title:      root_failed_alist/Failed_AList_Distinct_Compose.thy *)

section \<open>Isolated distinct_compose\<close>

theory Failed_AList_Distinct_Compose
  imports Main
begin

context
begin

subsection \<open>\<open>delete\<close>\<close>

qualified definition delete :: "'key \<Rightarrow> ('key \<times> 'val) list \<Rightarrow> ('key \<times> 'val) list"
  where delete_eq: "delete k = filter (\<lambda>(k', _). k \<noteq> k')"

lemma delete_simps [simp]:
  "delete k [] = []"
  "delete k (p # ps) = (if fst p = k then delete k ps else p # delete k ps)"
  by (auto simp add: delete_eq)

lemma delete_keys: "map fst (delete k al) = removeAll k (map fst al)"
  by (simp add: delete_eq removeAll_filter_not_eq filter_map split_def comp_def)

lemma distinct_delete:
  assumes "distinct (map fst al)"
  shows "distinct (map fst (delete k al))"
  using assms by (simp add: delete_keys distinct_removeAll)

lemma delete_id [simp]: "k \<notin> fst ` set al \<Longrightarrow> delete k al = al"
  by (auto simp add: image_iff delete_eq filter_id_conv)

lemma dom_delete_subset: "fst ` set (delete k al) \<subseteq> fst ` set al"
  by (auto simp add: delete_eq)

lemma length_delete_le: "length (delete k al) \<le> length al"
  by (simp add: delete_eq)

subsection \<open>\<open>compose\<close>\<close>

qualified function compose :: "('key \<times> 'a) list \<Rightarrow> ('a \<times> 'b) list \<Rightarrow> ('key \<times> 'b) list"
  where
    "compose [] ys = []"
  | "compose (x # xs) ys =
      (case map_of ys (snd x) of
        None \<Rightarrow> compose (delete (fst x) xs) ys
      | Some v \<Rightarrow> (fst x, v) # compose xs ys)"
  by pat_completeness auto
termination
  by (relation "measure (length \<circ> fst)") (simp_all add: less_Suc_eq_le length_delete_le)

lemma dom_compose: "fst ` set (compose xs ys) \<subseteq> fst ` set xs"
proof (induct xs ys rule: compose.induct)
  case 1
  then show ?case by simp
next
  case (2 x xs ys)
  show ?case
  proof (cases "map_of ys (snd x)")
    case None
    with "2.hyps" have "fst ` set (compose (delete (fst x) xs) ys) \<subseteq> fst ` set (delete (fst x) xs)"
      by simp
    also have "\<dots> \<subseteq> fst ` set xs"
      by (rule dom_delete_subset)
    finally show ?thesis
      using None by auto
  next
    case (Some v)
    with "2.hyps" have "fst ` set (compose xs ys) \<subseteq> fst ` set xs"
      by simp
    with Some show ?thesis
      by auto
  qed
qed

lemma distinct_compose:
  assumes "distinct (map fst xs)"
  shows "distinct (map fst (compose xs ys))"
  using assms
proof (induct xs ys rule: compose.induct)
  case 1
  then show ?case by simp
next
  case (2 x xs ys)
  show ?case
  proof (cases "map_of ys (snd x)")
    case None
    with 2 show ?thesis by simp
  next
    case (Some v)
    with 2 dom_compose [of xs ys] show ?thesis
      by auto
  qed
qed

end

end
