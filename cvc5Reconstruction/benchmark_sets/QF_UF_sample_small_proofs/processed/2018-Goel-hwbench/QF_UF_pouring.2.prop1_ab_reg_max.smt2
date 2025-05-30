(set-info :smt-lib-version 2.6)
(set-logic QF_UF)
(set-info :source |
Generated by: Aman Goel (amangoel@umich.edu), Karem A. Sakallah (karem@umich.edu)
Generated on: 2018-04-06

Generated by the tool Averroes 2 (successor of [1]) which implements safety property
verification on hardware systems.

This SMT problem belongs to a set of SMT problems generated by applying Averroes 2
to benchmarks derived from [2-5].

A total of 412 systems (345 from [2], 19 from [3], 26 from [4], 22 from [5]) were
syntactically converted from their original formats (using [6, 7]), and given to 
Averroes 2 to perform property checking with abstraction (wide bit-vectors -> terms, 
wide operators -> UF) using SMT solvers [8, 9].

[1] Lee S., Sakallah K.A. (2014) Unbounded Scalable Verification Based on Approximate
Property-Directed Reachability and Datapath Abstraction. In: Biere A., Bloem R. (eds)
Computer Aided Verification. CAV 2014. Lecture Notes in Computer Science, vol 8559.
Springer, Cham
[2] http://fmv.jku.at/aiger/index.html#beem
[3] http://www.cs.cmu.edu/~modelcheck/vcegar
[4] http://www.cprover.org/hardware/v2c
[5] http://github.com/aman-goel/verilogbench
[6] http://www.clifford.at/yosys
[7] http://github.com/chengyinwu/V3
[8] http://github.com/Z3Prover/z3
[9] http://github.com/SRI-CSL/yices2

id: pouring.2.prop1
query-maker: "Yices 2"
query-time: 0.002000 ms
query-class: abstract
query-category: oneshot
query-type: regular
status: unsat
|)
(set-info :license "https://creativecommons.org/licenses/by/4.0/")
(set-info :category "industrial")
(set-info :status unsat)
(declare-fun y$1 () Bool)
(declare-fun y$101 () Bool)
(declare-fun y$103 () Bool)
(declare-fun y$11 () Bool)
(declare-fun y$13 () Bool)
(declare-fun y$15 () Bool)
(declare-fun y$17 () Bool)
(declare-fun y$19 () Bool)
(declare-fun y$21 () Bool)
(declare-fun y$23 () Bool)
(declare-fun y$25 () Bool)
(declare-fun y$27 () Bool)
(declare-fun y$29 () Bool)
(declare-fun y$3 () Bool)
(declare-fun y$31 () Bool)
(declare-fun y$33 () Bool)
(declare-fun y$35 () Bool)
(declare-fun y$37 () Bool)
(declare-fun y$39 () Bool)
(declare-fun y$41 () Bool)
(declare-fun y$43 () Bool)
(declare-fun y$45 () Bool)
(declare-fun y$47 () Bool)
(declare-fun y$49 () Bool)
(declare-fun y$5 () Bool)
(declare-fun y$51 () Bool)
(declare-fun y$53 () Bool)
(declare-fun y$55 () Bool)
(declare-fun y$55378 () Bool)
(declare-fun y$55379 () Bool)
(declare-fun y$57 () Bool)
(declare-fun y$57110 () Bool)
(declare-fun y$57117 () Bool)
(declare-fun y$59 () Bool)
(declare-fun y$61 () Bool)
(declare-fun y$63 () Bool)
(declare-fun y$65 () Bool)
(declare-fun y$67 () Bool)
(declare-fun y$69 () Bool)
(declare-fun y$7 () Bool)
(declare-fun y$71 () Bool)
(declare-fun y$73 () Bool)
(declare-fun y$75 () Bool)
(declare-fun y$77 () Bool)
(declare-fun y$79 () Bool)
(declare-fun y$81 () Bool)
(declare-fun y$83 () Bool)
(declare-fun y$85 () Bool)
(declare-fun y$87 () Bool)
(declare-fun y$89 () Bool)
(declare-fun y$9 () Bool)
(declare-fun y$91 () Bool)
(declare-fun y$93 () Bool)
(declare-fun y$95 () Bool)
(declare-fun y$97 () Bool)
(declare-fun y$99 () Bool)
(declare-fun y$a_q0_Bottle_1 () Bool)
(declare-fun y$a_q0_Bottle_2 () Bool)
(declare-fun y$a_q0_Bottle_3 () Bool)
(declare-fun y$a_q0_Bottle_4 () Bool)
(declare-fun y$a_q0_Bottle_5 () Bool)
(declare-fun y$a_q10_Bottle_1 () Bool)
(declare-fun y$a_q10_Bottle_3 () Bool)
(declare-fun y$a_q11 () Bool)
(declare-fun y$a_q12 () Bool)
(declare-fun y$a_q13 () Bool)
(declare-fun y$a_q14 () Bool)
(declare-fun y$a_q1_Bottle_1 () Bool)
(declare-fun y$a_q1_Bottle_2 () Bool)
(declare-fun y$a_q1_Bottle_3 () Bool)
(declare-fun y$a_q1_Bottle_4 () Bool)
(declare-fun y$a_q1_Bottle_5 () Bool)
(declare-fun y$a_q2_Bottle_1 () Bool)
(declare-fun y$a_q2_Bottle_2 () Bool)
(declare-fun y$a_q2_Bottle_3 () Bool)
(declare-fun y$a_q2_Bottle_4 () Bool)
(declare-fun y$a_q2_Bottle_5 () Bool)
(declare-fun y$a_q3_Bottle_1 () Bool)
(declare-fun y$a_q3_Bottle_2 () Bool)
(declare-fun y$a_q3_Bottle_3 () Bool)
(declare-fun y$a_q3_Bottle_4 () Bool)
(declare-fun y$a_q3_Bottle_5 () Bool)
(declare-fun y$a_q4_Bottle_1 () Bool)
(declare-fun y$a_q4_Bottle_2 () Bool)
(declare-fun y$a_q4_Bottle_3 () Bool)
(declare-fun y$a_q4_Bottle_4 () Bool)
(declare-fun y$a_q4_Bottle_5 () Bool)
(declare-fun y$a_q5_Bottle_1 () Bool)
(declare-fun y$a_q5_Bottle_2 () Bool)
(declare-fun y$a_q5_Bottle_3 () Bool)
(declare-fun y$a_q5_Bottle_4 () Bool)
(declare-fun y$a_q5_Bottle_5 () Bool)
(declare-fun y$a_q6_Bottle_1 () Bool)
(declare-fun y$a_q6_Bottle_2 () Bool)
(declare-fun y$a_q6_Bottle_3 () Bool)
(declare-fun y$a_q6_Bottle_4 () Bool)
(declare-fun y$a_q7_Bottle_1 () Bool)
(declare-fun y$a_q7_Bottle_2 () Bool)
(declare-fun y$a_q7_Bottle_3 () Bool)
(declare-fun y$a_q7_Bottle_4 () Bool)
(declare-fun y$a_q8_Bottle_1 () Bool)
(declare-fun y$a_q8_Bottle_2 () Bool)
(declare-fun y$a_q8_Bottle_3 () Bool)
(declare-fun y$a_q9_Bottle_1 () Bool)
(declare-fun y$a_q9_Bottle_3 () Bool)
(declare-fun y$a_q_Sink () Bool)
(declare-fun y$a_q_Source () Bool)
(declare-fun y$dve_invalid () Bool)
(declare-fun y$id54 () Bool)
(declare-fun y$id54_op () Bool)
(declare-fun y$prop () Bool)
(assert (= y$a_q0_Bottle_1 (not y$1)))
(assert (= y$a_q0_Bottle_2 (not y$3)))
(assert (= y$a_q0_Bottle_3 (not y$5)))
(assert (= y$a_q0_Bottle_4 (not y$7)))
(assert (= y$a_q0_Bottle_5 (not y$9)))
(assert (= y$a_q10_Bottle_1 (not y$11)))
(assert (= y$a_q10_Bottle_3 (not y$13)))
(assert (= y$a_q11 (not y$15)))
(assert (= y$a_q12 (not y$17)))
(assert (= y$a_q13 (not y$19)))
(assert (= y$a_q14 (not y$21)))
(assert (= y$a_q1_Bottle_1 (not y$23)))
(assert (= y$a_q1_Bottle_2 (not y$25)))
(assert (= y$a_q1_Bottle_3 (not y$27)))
(assert (= y$a_q1_Bottle_4 (not y$29)))
(assert (= y$a_q1_Bottle_5 (not y$31)))
(assert (= y$a_q2_Bottle_1 (not y$33)))
(assert (= y$a_q2_Bottle_2 (not y$35)))
(assert (= y$a_q2_Bottle_3 (not y$37)))
(assert (= y$a_q2_Bottle_4 (not y$39)))
(assert (= y$a_q2_Bottle_5 (not y$41)))
(assert (= y$a_q3_Bottle_1 (not y$43)))
(assert (= y$a_q3_Bottle_2 (not y$45)))
(assert (= y$a_q3_Bottle_3 (not y$47)))
(assert (= y$a_q3_Bottle_4 (not y$49)))
(assert (= y$a_q3_Bottle_5 (not y$51)))
(assert (= y$a_q4_Bottle_1 (not y$53)))
(assert (= y$a_q4_Bottle_2 (not y$55)))
(assert (= y$a_q4_Bottle_3 (not y$57)))
(assert (= y$a_q4_Bottle_4 (not y$59)))
(assert (= y$a_q4_Bottle_5 (not y$61)))
(assert (= y$a_q5_Bottle_1 (not y$63)))
(assert (= y$a_q5_Bottle_2 (not y$65)))
(assert (= y$a_q5_Bottle_3 (not y$67)))
(assert (= y$a_q5_Bottle_4 (not y$69)))
(assert (= y$a_q5_Bottle_5 (not y$71)))
(assert (= y$a_q6_Bottle_1 (not y$73)))
(assert (= y$a_q6_Bottle_2 (not y$75)))
(assert (= y$a_q6_Bottle_3 (not y$77)))
(assert (= y$a_q6_Bottle_4 (not y$79)))
(assert (= y$a_q7_Bottle_1 (not y$81)))
(assert (= y$a_q7_Bottle_2 (not y$83)))
(assert (= y$a_q7_Bottle_3 (not y$85)))
(assert (= y$a_q7_Bottle_4 (not y$87)))
(assert (= y$a_q8_Bottle_1 (not y$89)))
(assert (= y$a_q8_Bottle_2 (not y$91)))
(assert (= y$a_q8_Bottle_3 (not y$93)))
(assert (= y$a_q9_Bottle_1 (not y$95)))
(assert (= y$a_q9_Bottle_3 (not y$97)))
(assert (= y$a_q_Sink (not y$99)))
(assert (= y$a_q_Source (not y$101)))
(assert (= y$dve_invalid (not y$103)))
(assert (= y$prop (not y$57110)))
(assert (= y$id54_op (and y$a_q4_Bottle_1 y$103)))
(assert (= y$id54_op (not y$55378)))
(assert (= y$55379 (= y$prop y$55378)))
(assert (= y$57117 (and y$1 y$3 y$5 y$7 y$9 y$11 y$13 y$15 y$17 y$19 y$21 y$23 y$25 y$27 y$29 y$31 y$33 y$35 y$37 y$39 y$41 y$43 y$45 y$47 y$49 y$51 y$53 y$55 y$57 y$59 y$61 y$63 y$65 y$67 y$69 y$71 y$73 y$75 y$77 y$79 y$81 y$83 y$85 y$87 y$89 y$91 y$93 y$95 y$97 y$99 y$101 y$103 y$57110 y$55379)))
(assert y$57117)
(check-sat)
(exit)
