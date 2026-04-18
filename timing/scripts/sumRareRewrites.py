#!/usr/bin/env python3
"""Sum up counts and totals of selected rare_rewrite rules from by-rule.csv files."""

import argparse
import csv
import sys

RULES = [
    "Arith_Rewrites.rewrite_arith_elim_gt",
    "Arith_Rewrites.rewrite_arith_elim_lt",
    "Arith_Rewrites.rewrite_arith_elim_int_gt",
    "Arith_Rewrites.rewrite_arith_elim_int_lt",
    "Arith_Rewrites.rewrite_arith_elim_leq",
    "Arith_Rewrites.rewrite_arith_leq_norm",
    "Arith_Rewrites.rewrite_arith_geq_tighten",
    "Arith_Rewrites.rewrite_arith_geq_norm1_int",
    "Arith_Rewrites.rewrite_arith_eq_elim_int",
    "Boolean_Rewrites.rewrite_bool_double_not_elim",
    "Boolean_Rewrites.rewrite_bool_not_true",
    "Boolean_Rewrites.rewrite_bool_not_false",
    "Boolean_Rewrites.rewrite_bool_eq_true",
    "Boolean_Rewrites.rewrite_bool_eq_false",
    "Boolean_Rewrites.rewrite_bool_eq_nrefl",
    "Boolean_Rewrites.rewrite_bool_impl_false1",
    "Boolean_Rewrites.rewrite_bool_impl_false2",
    "Boolean_Rewrites.rewrite_bool_impl_true1",
    "Boolean_Rewrites.rewrite_bool_impl_true2",
    "Boolean_Rewrites.rewrite_bool_impl_elim",
    "Boolean_Rewrites.rewrite_bool_dual_impl_eq",
    "Boolean_Rewrites.rewrite_bool_implies_de_morgan",
    "Boolean_Rewrites.rewrite_bool_xor_refl",
    "Boolean_Rewrites.rewrite_bool_xor_nrefl",
    "Boolean_Rewrites.rewrite_bool_xor_false",
    "Boolean_Rewrites.rewrite_bool_xor_true",
    "Boolean_Rewrites.rewrite_bool_xor_comm",
    "Boolean_Rewrites.rewrite_bool_xor_elim",
    "Boolean_Rewrites.rewrite_bool_not_xor_elim",
    "Boolean_Rewrites.rewrite_bool_not_eq_elim1",
    "Boolean_Rewrites.rewrite_bool_not_eq_elim2",
    "Boolean_Rewrites.rewrite_ite_neg_branch",
    "Boolean_Rewrites.rewrite_ite_then_true",
    "Boolean_Rewrites.rewrite_ite_else_false",
    "Boolean_Rewrites.rewrite_ite_then_false",
    "Boolean_Rewrites.rewrite_ite_else_true",
    "Boolean_Rewrites.rewrite_ite_then_lookahead_self",
    "Boolean_Rewrites.rewrite_ite_else_lookahead_self",
    "Boolean_Rewrites.rewrite_ite_then_lookahead_not_self",
    "Boolean_Rewrites.rewrite_ite_else_lookahead_not_self",
    "Boolean_Rewrites.rewrite_ite_expand",
    "Boolean_Rewrites.rewrite_bool_not_ite_elim",
    "Builtin_Rewrites.rewrite_ite_true_cond",
    "Builtin_Rewrites.rewrite_ite_false_cond",
    "Builtin_Rewrites.rewrite_ite_not_cond",
    "Builtin_Rewrites.rewrite_ite_eq_branch",
    "Builtin_Rewrites.rewrite_ite_then_lookahead",
    "Builtin_Rewrites.rewrite_ite_else_lookahead",
    "Builtin_Rewrites.rewrite_ite_then_neg_lookahead",
    "Builtin_Rewrites.rewrite_ite_else_neg_lookahead",
    "UF_Rewrites.rewrite_eq_refl",
    "UF_Rewrites.rewrite_eq_symm",
    "UF_Rewrites.rewrite_eq_cond_deq",
    "UF_Rewrites.rewrite_eq_ite_lift",
    "UF_Rewrites.rewrite_distinct_binary_elim",
    "cvc5_Rewrites.rewrite_ite_eq",
    "cvc5_Rewrites.rewrite_distinct_binary_elim",
    "cvc5_Rewrites.rewrite_bool_not_eq_false",
    "Rare_Interface_Real.rewrite_arith_geq_norm1_real",
    "Rare_Interface_Real.rewrite_arith_eq_elim_real",
    "Rare_Interface_Real.rewrite_arith_to_int_to_real",
    "Rare_Interface_Real.rewrite_arith_int_eq_conflict",
    "Rare_Interface_Real.rewrite_arith_int_geq_tighten",
    "Rare_Interface_Real.rewrite_arith_geq_ite_lift",
    "Rare_Interface_Real.rewrite_arith_leq_ite_lift",
]


def to_csv_rule_name(qualified_rule: str) -> str:
    """Convert 'Arith_Rewrites.rewrite_arith_elim_gt' to 'rare_rewrite_arith-elim-gt'."""
    bare = qualified_rule.split(".", 1)[1]
    assert bare.startswith("rewrite_"), f"unexpected rule name: {qualified_rule}"
    suffix = bare[len("rewrite_"):].replace("_", "-")
    return f"rare_rewrite_{suffix}"


def process_file(path: str, target_rules: set[str], verbose: bool) -> None:
    simple_count = 0
    simple_time = 0
    complex_count = 0
    complex_time = 0
    simple_matched = set()
    complex_rules = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rule = row["rule"]
            if not rule.startswith("rare_rewrite"):
                continue
            count = int(row["count"])
            total = int(row["total"])
            if rule in target_rules:
                simple_matched.add(rule)
                simple_count += count
                simple_time += total
            else:
                complex_count += count
                complex_time += total
                complex_rules.append(rule)

    print(f"=== {path} ===")
    simple_time_s = simple_time / 1e9
    complex_time_s = complex_time / 1e9

    print("simple rewrites:")
    print(f"  sum of count:      {simple_count}")
    print(f"  sum of total (s):  {simple_time_s:.2f}")
    if simple_count > 0:
        print(f"  mean (ms/rewrite): {simple_time_s * 1000 / simple_count:.2f}")
    print("complex rewrites:")
    print(f"  sum of count:      {complex_count}")
    print(f"  sum of total (s):  {complex_time_s:.2f}")
    if complex_count > 0:
        print(f"  mean (ms/rewrite): {complex_time_s * 1000 / complex_count:.2f}")

    if verbose:
        missing = sorted(target_rules - simple_matched)
        if missing:
            print("\nrules in list but not found in CSV:")
            for r in missing:
                print(f"  {r}")
        if complex_rules:
            print("\ncomplex rewrite rules found in CSV:")
            for r in sorted(complex_rules):
                print(f"  {r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", help="by-rule.csv files to process")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="list rules from the target list that were not found")
    args = parser.parse_args()

    target_rules = {to_csv_rule_name(r) for r in RULES}

    for path in args.files:
        process_file(path, target_rules, args.verbose)

    return 0


if __name__ == "__main__":
    sys.exit(main())
