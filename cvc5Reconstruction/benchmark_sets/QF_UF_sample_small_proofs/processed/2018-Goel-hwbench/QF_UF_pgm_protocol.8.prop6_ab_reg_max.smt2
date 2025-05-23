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

id: pgm_protocol.8.prop6
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
(declare-sort utt$8 0)
(declare-sort utt$24 0)
(declare-sort utt$32 0)
(declare-fun Concat_32_8_24 (utt$8 utt$24) utt$32)
(declare-fun GrEq_1_32_32 (utt$32 utt$32) Bool)
(declare-fun y$1 () Bool)
(declare-fun y$101 () Bool)
(declare-fun y$103 () Bool)
(declare-fun y$105 () Bool)
(declare-fun y$107 () Bool)
(declare-fun y$109 () Bool)
(declare-fun y$11 () Bool)
(declare-fun y$111 () Bool)
(declare-fun y$114 () Bool)
(declare-fun y$116 () Bool)
(declare-fun y$118 () Bool)
(declare-fun y$120 () Bool)
(declare-fun y$122 () Bool)
(declare-fun y$124 () Bool)
(declare-fun y$126 () Bool)
(declare-fun y$128 () Bool)
(declare-fun y$13 () Bool)
(declare-fun y$130 () Bool)
(declare-fun y$132 () Bool)
(declare-fun y$134 () Bool)
(declare-fun y$136 () Bool)
(declare-fun y$138 () Bool)
(declare-fun y$140 () Bool)
(declare-fun y$142 () Bool)
(declare-fun y$144 () Bool)
(declare-fun y$146 () Bool)
(declare-fun y$148 () Bool)
(declare-fun y$15 () Bool)
(declare-fun y$150 () Bool)
(declare-fun y$152 () Bool)
(declare-fun y$154 () Bool)
(declare-fun y$156 () Bool)
(declare-fun y$158 () Bool)
(declare-fun y$160 () Bool)
(declare-fun y$162 () Bool)
(declare-fun y$164 () Bool)
(declare-fun y$166 () Bool)
(declare-fun y$168 () Bool)
(declare-fun y$17 () Bool)
(declare-fun y$170 () Bool)
(declare-fun y$172 () Bool)
(declare-fun y$174 () Bool)
(declare-fun y$176 () Bool)
(declare-fun y$178 () Bool)
(declare-fun y$180 () Bool)
(declare-fun y$182 () Bool)
(declare-fun y$184 () Bool)
(declare-fun y$186 () Bool)
(declare-fun y$188 () Bool)
(declare-fun y$19 () Bool)
(declare-fun y$190 () Bool)
(declare-fun y$192 () Bool)
(declare-fun y$194 () Bool)
(declare-fun y$196 () Bool)
(declare-fun y$198 () Bool)
(declare-fun y$200 () Bool)
(declare-fun y$202 () Bool)
(declare-fun y$204 () Bool)
(declare-fun y$206 () Bool)
(declare-fun y$208 () Bool)
(declare-fun y$21 () Bool)
(declare-fun y$210 () Bool)
(declare-fun y$212 () Bool)
(declare-fun y$214 () Bool)
(declare-fun y$216 () Bool)
(declare-fun y$218 () Bool)
(declare-fun y$220 () Bool)
(declare-fun y$222 () Bool)
(declare-fun y$224 () Bool)
(declare-fun y$226 () Bool)
(declare-fun y$228 () Bool)
(declare-fun y$23 () Bool)
(declare-fun y$230 () Bool)
(declare-fun y$232 () Bool)
(declare-fun y$234 () Bool)
(declare-fun y$236 () Bool)
(declare-fun y$238 () Bool)
(declare-fun y$240 () Bool)
(declare-fun y$242 () Bool)
(declare-fun y$244 () Bool)
(declare-fun y$246 () Bool)
(declare-fun y$248 () Bool)
(declare-fun y$25 () Bool)
(declare-fun y$250 () Bool)
(declare-fun y$252 () Bool)
(declare-fun y$254 () Bool)
(declare-fun y$256 () Bool)
(declare-fun y$258 () Bool)
(declare-fun y$260 () Bool)
(declare-fun y$262 () Bool)
(declare-fun y$264 () Bool)
(declare-fun y$266 () Bool)
(declare-fun y$268 () Bool)
(declare-fun y$27 () Bool)
(declare-fun y$270 () Bool)
(declare-fun y$272 () Bool)
(declare-fun y$274 () Bool)
(declare-fun y$276 () Bool)
(declare-fun y$278 () Bool)
(declare-fun y$280 () Bool)
(declare-fun y$282 () Bool)
(declare-fun y$284 () Bool)
(declare-fun y$286 () Bool)
(declare-fun y$288 () Bool)
(declare-fun y$29 () Bool)
(declare-fun y$290 () Bool)
(declare-fun y$292 () Bool)
(declare-fun y$294 () Bool)
(declare-fun y$296 () Bool)
(declare-fun y$298 () Bool)
(declare-fun y$3 () Bool)
(declare-fun y$300 () Bool)
(declare-fun y$302 () Bool)
(declare-fun y$304 () Bool)
(declare-fun y$306 () Bool)
(declare-fun y$308 () Bool)
(declare-fun y$31 () Bool)
(declare-fun y$310 () Bool)
(declare-fun y$312 () Bool)
(declare-fun y$314 () Bool)
(declare-fun y$316 () Bool)
(declare-fun y$318 () Bool)
(declare-fun y$320 () Bool)
(declare-fun y$322 () Bool)
(declare-fun y$324 () Bool)
(declare-fun y$326 () Bool)
(declare-fun y$328 () Bool)
(declare-fun y$33 () Bool)
(declare-fun y$330 () Bool)
(declare-fun y$332 () Bool)
(declare-fun y$334 () Bool)
(declare-fun y$336 () Bool)
(declare-fun y$338 () Bool)
(declare-fun y$340 () Bool)
(declare-fun y$342 () Bool)
(declare-fun y$344 () Bool)
(declare-fun y$346 () Bool)
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
(declare-fun y$57 () Bool)
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
(declare-fun y$9176 () Bool)
(declare-fun y$9177 () Bool)
(declare-fun y$93 () Bool)
(declare-fun y$9304 () Bool)
(declare-fun y$9317 () Bool)
(declare-fun y$95 () Bool)
(declare-fun y$97 () Bool)
(declare-fun y$99 () Bool)
(declare-fun y$a_e0 () Bool)
(declare-fun y$a_e0_1 () Bool)
(declare-fun y$a_e0_2 () Bool)
(declare-fun y$a_e1 () Bool)
(declare-fun y$a_e_nak () Bool)
(declare-fun y$a_e_odata () Bool)
(declare-fun y$a_e_odata1 () Bool)
(declare-fun y$a_e_odata2 () Bool)
(declare-fun y$a_e_rdata () Bool)
(declare-fun y$a_e_rdata1 () Bool)
(declare-fun y$a_e_rdata2 () Bool)
(declare-fun y$a_e_spm () Bool)
(declare-fun y$a_e_spm1 () Bool)
(declare-fun y$a_e_spm2 () Bool)
(declare-fun y$a_q_NR () Bool)
(declare-fun y$a_q_NS () Bool)
(declare-fun y$a_q_RN () Bool)
(declare-fun y$a_q_SN () Bool)
(declare-fun y$a_q_in_1_NR () Bool)
(declare-fun y$a_q_in_1_NS () Bool)
(declare-fun y$a_q_in_1_RN () Bool)
(declare-fun y$a_q_in_1_SN () Bool)
(declare-fun y$a_q_in_2_NR () Bool)
(declare-fun y$a_q_in_2_SN () Bool)
(declare-fun y$a_q_in_3_NR () Bool)
(declare-fun y$a_q_in_3_SN () Bool)
(declare-fun y$a_q_out_1_NR () Bool)
(declare-fun y$a_q_out_1_NS () Bool)
(declare-fun y$a_q_out_1_RN () Bool)
(declare-fun y$a_q_out_1_SN () Bool)
(declare-fun y$a_q_out_2_NR () Bool)
(declare-fun y$a_q_out_2_SN () Bool)
(declare-fun y$a_q_out_3_NR () Bool)
(declare-fun y$a_q_out_3_SN () Bool)
(declare-fun y$a_r0 () Bool)
(declare-fun y$a_r0_1 () Bool)
(declare-fun y$a_r0_2 () Bool)
(declare-fun y$a_r1 () Bool)
(declare-fun y$a_r2 () Bool)
(declare-fun y$a_r3 () Bool)
(declare-fun y$a_r4 () Bool)
(declare-fun y$a_r_out () Bool)
(declare-fun y$a_r_tmp () Bool)
(declare-fun y$a_r_trail () Bool)
(declare-fun y$a_s0 () Bool)
(declare-fun y$a_s0_1 () Bool)
(declare-fun y$a_s0_2 () Bool)
(declare-fun y$a_s0_3 () Bool)
(declare-fun y$a_s0_4 () Bool)
(declare-fun y$a_s0_5 () Bool)
(declare-fun y$a_s0_6 () Bool)
(declare-fun y$a_s1 () Bool)
(declare-fun y$a_s1_1 () Bool)
(declare-fun y$a_s1_2 () Bool)
(declare-fun y$a_tick () Bool)
(declare-fun y$dve_invalid () Bool)
(declare-fun y$id185 () Bool)
(declare-fun y$id185_op () Bool)
(declare-fun y$n0s24 () utt$24)
(declare-fun y$n0s32 () utt$32)
(declare-fun y$n0s8 () utt$8)
(declare-fun y$n12s32 () utt$32)
(declare-fun y$n12s8 () utt$8)
(declare-fun y$n1s32 () utt$32)
(declare-fun y$n1s8 () utt$8)
(declare-fun y$n2s32 () utt$32)
(declare-fun y$n2s8 () utt$8)
(declare-fun y$n3s32 () utt$32)
(declare-fun y$n3s8 () utt$8)
(declare-fun y$n4s32 () utt$32)
(declare-fun y$n4s8 () utt$8)
(declare-fun y$n5s32 () utt$32)
(declare-fun y$n5s8 () utt$8)
(declare-fun y$n6s32 () utt$32)
(declare-fun y$n6s8 () utt$8)
(declare-fun y$n7s32 () utt$32)
(declare-fun y$n7s8 () utt$8)
(declare-fun y$n9s8 () utt$8)
(declare-fun y$prop () Bool)
(declare-fun y$v3_1517448504_182 () Bool)
(declare-fun y$v3_1517448504_182_op () Bool)
(declare-fun y$v3_1517448504_183 () Bool)
(declare-fun y$v3_1517448504_183_op () Bool)
(declare-fun y$v_NR_size () utt$8)
(declare-fun y$v_NR_time_0 () utt$8)
(declare-fun y$v_NR_time_1 () utt$8)
(declare-fun y$v_NR_time_2 () utt$8)
(declare-fun y$v_NR_time_3 () utt$8)
(declare-fun y$v_NR_time_4 () utt$8)
(declare-fun y$v_NR_time_5 () utt$8)
(declare-fun y$v_NR_time_6 () utt$8)
(declare-fun y$v_NS_size () utt$8)
(declare-fun y$v_NS_time_0 () utt$8)
(declare-fun y$v_NS_time_1 () utt$8)
(declare-fun y$v_NS_time_2 () utt$8)
(declare-fun y$v_NS_time_3 () utt$8)
(declare-fun y$v_NS_time_4 () utt$8)
(declare-fun y$v_NS_time_5 () utt$8)
(declare-fun y$v_NS_time_6 () utt$8)
(declare-fun y$v_RN_size () utt$8)
(declare-fun y$v_RN_time_0 () utt$8)
(declare-fun y$v_RN_time_1 () utt$8)
(declare-fun y$v_RN_time_2 () utt$8)
(declare-fun y$v_RN_time_3 () utt$8)
(declare-fun y$v_RN_time_4 () utt$8)
(declare-fun y$v_RN_time_5 () utt$8)
(declare-fun y$v_RN_time_6 () utt$8)
(declare-fun y$v_RXW_0 () utt$8)
(declare-fun y$v_RXW_1 () utt$8)
(declare-fun y$v_RXW_2 () utt$8)
(declare-fun y$v_RXW_3 () utt$8)
(declare-fun y$v_RXW_4 () utt$8)
(declare-fun y$v_RXW_LEAD () utt$8)
(declare-fun y$v_RXW_TRAIL () utt$8)
(declare-fun y$v_SN_size () utt$8)
(declare-fun y$v_SN_time_0 () utt$8)
(declare-fun y$v_SN_time_1 () utt$8)
(declare-fun y$v_SN_time_2 () utt$8)
(declare-fun y$v_SN_time_3 () utt$8)
(declare-fun y$v_SN_time_4 () utt$8)
(declare-fun y$v_SN_time_5 () utt$8)
(declare-fun y$v_SN_time_6 () utt$8)
(declare-fun y$v_TXW_LEAD () utt$8)
(declare-fun y$v_TXW_TRAIL () utt$8)
(declare-fun y$v_buf_0_NR_0 () utt$8)
(declare-fun y$v_buf_0_NR_1 () utt$8)
(declare-fun y$v_buf_0_NR_2 () utt$8)
(declare-fun y$v_buf_0_NR_3 () utt$8)
(declare-fun y$v_buf_0_NR_4 () utt$8)
(declare-fun y$v_buf_0_NR_5 () utt$8)
(declare-fun y$v_buf_0_NR_6 () utt$8)
(declare-fun y$v_buf_0_NS_0 () utt$8)
(declare-fun y$v_buf_0_NS_1 () utt$8)
(declare-fun y$v_buf_0_NS_2 () utt$8)
(declare-fun y$v_buf_0_NS_3 () utt$8)
(declare-fun y$v_buf_0_NS_4 () utt$8)
(declare-fun y$v_buf_0_NS_5 () utt$8)
(declare-fun y$v_buf_0_NS_6 () utt$8)
(declare-fun y$v_buf_0_RN_0 () utt$8)
(declare-fun y$v_buf_0_RN_1 () utt$8)
(declare-fun y$v_buf_0_RN_2 () utt$8)
(declare-fun y$v_buf_0_RN_3 () utt$8)
(declare-fun y$v_buf_0_RN_4 () utt$8)
(declare-fun y$v_buf_0_RN_5 () utt$8)
(declare-fun y$v_buf_0_RN_6 () utt$8)
(declare-fun y$v_buf_0_SN_0 () utt$8)
(declare-fun y$v_buf_0_SN_1 () utt$8)
(declare-fun y$v_buf_0_SN_2 () utt$8)
(declare-fun y$v_buf_0_SN_3 () utt$8)
(declare-fun y$v_buf_0_SN_4 () utt$8)
(declare-fun y$v_buf_0_SN_5 () utt$8)
(declare-fun y$v_buf_0_SN_6 () utt$8)
(declare-fun y$v_buf_1_NR_0 () utt$8)
(declare-fun y$v_buf_1_NR_1 () utt$8)
(declare-fun y$v_buf_1_NR_2 () utt$8)
(declare-fun y$v_buf_1_NR_3 () utt$8)
(declare-fun y$v_buf_1_NR_4 () utt$8)
(declare-fun y$v_buf_1_NR_5 () utt$8)
(declare-fun y$v_buf_1_NR_6 () utt$8)
(declare-fun y$v_buf_1_SN_0 () utt$8)
(declare-fun y$v_buf_1_SN_1 () utt$8)
(declare-fun y$v_buf_1_SN_2 () utt$8)
(declare-fun y$v_buf_1_SN_3 () utt$8)
(declare-fun y$v_buf_1_SN_4 () utt$8)
(declare-fun y$v_buf_1_SN_5 () utt$8)
(declare-fun y$v_buf_1_SN_6 () utt$8)
(declare-fun y$v_buf_2_NR_0 () utt$8)
(declare-fun y$v_buf_2_NR_1 () utt$8)
(declare-fun y$v_buf_2_NR_2 () utt$8)
(declare-fun y$v_buf_2_NR_3 () utt$8)
(declare-fun y$v_buf_2_NR_4 () utt$8)
(declare-fun y$v_buf_2_NR_5 () utt$8)
(declare-fun y$v_buf_2_NR_6 () utt$8)
(declare-fun y$v_buf_2_SN_0 () utt$8)
(declare-fun y$v_buf_2_SN_1 () utt$8)
(declare-fun y$v_buf_2_SN_2 () utt$8)
(declare-fun y$v_buf_2_SN_3 () utt$8)
(declare-fun y$v_buf_2_SN_4 () utt$8)
(declare-fun y$v_buf_2_SN_5 () utt$8)
(declare-fun y$v_buf_2_SN_6 () utt$8)
(declare-fun y$v_c () utt$8)
(declare-fun y$v_close () utt$8)
(declare-fun y$v_i () utt$8)
(declare-fun y$v_nloss () utt$8)
(declare-fun y$v_packet_element () utt$8)
(declare-fun y$v_packet_global () utt$8)
(declare-fun y$v_packet_receiver () utt$8)
(declare-fun y$v_rs_0 () utt$8)
(declare-fun y$v_rs_1 () utt$8)
(declare-fun y$v_rs_2 () utt$8)
(declare-fun y$v_rs_3 () utt$8)
(declare-fun y$v_rs_4 () utt$8)
(declare-fun y$v_rs_5 () utt$8)
(declare-fun y$v_rs_len () utt$8)
(declare-fun y$v_seq () utt$8)
(declare-fun y$v_sqn_global () utt$8)
(declare-fun y$v_sqn_receiver () utt$8)
(declare-fun y$v_trail_element () utt$8)
(declare-fun y$v_trail_receiver () utt$8)
(declare-fun y$v_x () utt$8)
(declare-fun y$w$55 () utt$32)
(declare-fun y$w$55_op () utt$32)
(assert (distinct y$n0s8 y$n3s8 y$n1s8 y$n2s8 y$n4s8 y$n5s8 y$n6s8 y$n9s8 y$n12s8 y$n7s8))
(assert (distinct y$n0s32 y$n1s32 y$n2s32 y$n3s32 y$n4s32 y$n5s32 y$n6s32 y$n12s32 y$n7s32))
(assert (= y$a_e0 (not y$1)))
(assert (= y$a_e0_1 (not y$3)))
(assert (= y$a_e0_2 (not y$5)))
(assert (= y$a_e1 (not y$7)))
(assert (= y$a_e_nak (not y$9)))
(assert (= y$a_e_odata (not y$11)))
(assert (= y$a_e_odata1 (not y$13)))
(assert (= y$a_e_odata2 (not y$15)))
(assert (= y$a_e_rdata (not y$17)))
(assert (= y$a_e_rdata1 (not y$19)))
(assert (= y$a_e_rdata2 (not y$21)))
(assert (= y$a_e_spm (not y$23)))
(assert (= y$a_e_spm1 (not y$25)))
(assert (= y$a_e_spm2 (not y$27)))
(assert (= y$a_q_NR (not y$29)))
(assert (= y$a_q_NS (not y$31)))
(assert (= y$a_q_RN (not y$33)))
(assert (= y$a_q_SN (not y$35)))
(assert (= y$a_q_in_1_NR (not y$37)))
(assert (= y$a_q_in_1_NS (not y$39)))
(assert (= y$a_q_in_1_RN (not y$41)))
(assert (= y$a_q_in_1_SN (not y$43)))
(assert (= y$a_q_in_2_NR (not y$45)))
(assert (= y$a_q_in_2_SN (not y$47)))
(assert (= y$a_q_in_3_NR (not y$49)))
(assert (= y$a_q_in_3_SN (not y$51)))
(assert (= y$a_q_out_1_NR (not y$53)))
(assert (= y$a_q_out_1_NS (not y$55)))
(assert (= y$a_q_out_1_RN (not y$57)))
(assert (= y$a_q_out_1_SN (not y$59)))
(assert (= y$a_q_out_2_NR (not y$61)))
(assert (= y$a_q_out_2_SN (not y$63)))
(assert (= y$a_q_out_3_NR (not y$65)))
(assert (= y$a_q_out_3_SN (not y$67)))
(assert (= y$a_r0 (not y$69)))
(assert (= y$a_r0_1 (not y$71)))
(assert (= y$a_r0_2 (not y$73)))
(assert (= y$a_r1 (not y$75)))
(assert (= y$a_r2 (not y$77)))
(assert (= y$a_r3 (not y$79)))
(assert (= y$a_r4 (not y$81)))
(assert (= y$a_r_out (not y$83)))
(assert (= y$a_r_tmp (not y$85)))
(assert (= y$a_r_trail (not y$87)))
(assert (= y$a_s0 (not y$89)))
(assert (= y$a_s0_1 (not y$91)))
(assert (= y$a_s0_2 (not y$93)))
(assert (= y$a_s0_3 (not y$95)))
(assert (= y$a_s0_4 (not y$97)))
(assert (= y$a_s0_5 (not y$99)))
(assert (= y$a_s0_6 (not y$101)))
(assert (= y$a_s1 (not y$103)))
(assert (= y$a_s1_1 (not y$105)))
(assert (= y$a_s1_2 (not y$107)))
(assert (= y$a_tick (not y$109)))
(assert (= y$dve_invalid (not y$111)))
(assert (= y$114 (= y$n0s8 y$v_NR_size)))
(assert (= y$116 (= y$n0s8 y$v_NR_time_0)))
(assert (= y$118 (= y$n0s8 y$v_NR_time_1)))
(assert (= y$120 (= y$n0s8 y$v_NR_time_2)))
(assert (= y$122 (= y$n0s8 y$v_NR_time_3)))
(assert (= y$124 (= y$n0s8 y$v_NR_time_4)))
(assert (= y$126 (= y$n0s8 y$v_NR_time_5)))
(assert (= y$128 (= y$n0s8 y$v_NR_time_6)))
(assert (= y$130 (= y$n0s8 y$v_NS_size)))
(assert (= y$132 (= y$n0s8 y$v_NS_time_0)))
(assert (= y$134 (= y$n0s8 y$v_NS_time_1)))
(assert (= y$136 (= y$n0s8 y$v_NS_time_2)))
(assert (= y$138 (= y$n0s8 y$v_NS_time_3)))
(assert (= y$140 (= y$n0s8 y$v_NS_time_4)))
(assert (= y$142 (= y$n0s8 y$v_NS_time_5)))
(assert (= y$144 (= y$n0s8 y$v_NS_time_6)))
(assert (= y$146 (= y$n0s8 y$v_RN_size)))
(assert (= y$148 (= y$n0s8 y$v_RN_time_0)))
(assert (= y$150 (= y$n0s8 y$v_RN_time_1)))
(assert (= y$152 (= y$n0s8 y$v_RN_time_2)))
(assert (= y$154 (= y$n0s8 y$v_RN_time_3)))
(assert (= y$156 (= y$n0s8 y$v_RN_time_4)))
(assert (= y$158 (= y$n0s8 y$v_RN_time_5)))
(assert (= y$160 (= y$n0s8 y$v_RN_time_6)))
(assert (= y$162 (= y$n0s8 y$v_RXW_0)))
(assert (= y$164 (= y$n0s8 y$v_RXW_1)))
(assert (= y$166 (= y$n0s8 y$v_RXW_2)))
(assert (= y$168 (= y$n0s8 y$v_RXW_3)))
(assert (= y$170 (= y$n0s8 y$v_RXW_4)))
(assert (= y$172 (= y$n0s8 y$v_RXW_LEAD)))
(assert (= y$174 (= y$n0s8 y$v_RXW_TRAIL)))
(assert (= y$176 (= y$n0s8 y$v_SN_size)))
(assert (= y$178 (= y$n0s8 y$v_SN_time_0)))
(assert (= y$180 (= y$n0s8 y$v_SN_time_1)))
(assert (= y$182 (= y$n0s8 y$v_SN_time_2)))
(assert (= y$184 (= y$n0s8 y$v_SN_time_3)))
(assert (= y$186 (= y$n0s8 y$v_SN_time_4)))
(assert (= y$188 (= y$n0s8 y$v_SN_time_5)))
(assert (= y$190 (= y$n0s8 y$v_SN_time_6)))
(assert (= y$192 (= y$n0s8 y$v_TXW_LEAD)))
(assert (= y$194 (= y$n0s8 y$v_TXW_TRAIL)))
(assert (= y$196 (= y$n0s8 y$v_buf_0_NR_0)))
(assert (= y$198 (= y$n0s8 y$v_buf_0_NR_1)))
(assert (= y$200 (= y$n0s8 y$v_buf_0_NR_2)))
(assert (= y$202 (= y$n0s8 y$v_buf_0_NR_3)))
(assert (= y$204 (= y$n0s8 y$v_buf_0_NR_4)))
(assert (= y$206 (= y$n0s8 y$v_buf_0_NR_5)))
(assert (= y$208 (= y$n0s8 y$v_buf_0_NR_6)))
(assert (= y$210 (= y$n0s8 y$v_buf_0_NS_0)))
(assert (= y$212 (= y$n0s8 y$v_buf_0_NS_1)))
(assert (= y$214 (= y$n0s8 y$v_buf_0_NS_2)))
(assert (= y$216 (= y$n0s8 y$v_buf_0_NS_3)))
(assert (= y$218 (= y$n0s8 y$v_buf_0_NS_4)))
(assert (= y$220 (= y$n0s8 y$v_buf_0_NS_5)))
(assert (= y$222 (= y$n0s8 y$v_buf_0_NS_6)))
(assert (= y$224 (= y$n0s8 y$v_buf_0_RN_0)))
(assert (= y$226 (= y$n0s8 y$v_buf_0_RN_1)))
(assert (= y$228 (= y$n0s8 y$v_buf_0_RN_2)))
(assert (= y$230 (= y$n0s8 y$v_buf_0_RN_3)))
(assert (= y$232 (= y$n0s8 y$v_buf_0_RN_4)))
(assert (= y$234 (= y$n0s8 y$v_buf_0_RN_5)))
(assert (= y$236 (= y$n0s8 y$v_buf_0_RN_6)))
(assert (= y$238 (= y$n0s8 y$v_buf_0_SN_0)))
(assert (= y$240 (= y$n0s8 y$v_buf_0_SN_1)))
(assert (= y$242 (= y$n0s8 y$v_buf_0_SN_2)))
(assert (= y$244 (= y$n0s8 y$v_buf_0_SN_3)))
(assert (= y$246 (= y$n0s8 y$v_buf_0_SN_4)))
(assert (= y$248 (= y$n0s8 y$v_buf_0_SN_5)))
(assert (= y$250 (= y$n0s8 y$v_buf_0_SN_6)))
(assert (= y$252 (= y$n0s8 y$v_buf_1_NR_0)))
(assert (= y$254 (= y$n0s8 y$v_buf_1_NR_1)))
(assert (= y$256 (= y$n0s8 y$v_buf_1_NR_2)))
(assert (= y$258 (= y$n0s8 y$v_buf_1_NR_3)))
(assert (= y$260 (= y$n0s8 y$v_buf_1_NR_4)))
(assert (= y$262 (= y$n0s8 y$v_buf_1_NR_5)))
(assert (= y$264 (= y$n0s8 y$v_buf_1_NR_6)))
(assert (= y$266 (= y$n0s8 y$v_buf_1_SN_0)))
(assert (= y$268 (= y$n0s8 y$v_buf_1_SN_1)))
(assert (= y$270 (= y$n0s8 y$v_buf_1_SN_2)))
(assert (= y$272 (= y$n0s8 y$v_buf_1_SN_3)))
(assert (= y$274 (= y$n0s8 y$v_buf_1_SN_4)))
(assert (= y$276 (= y$n0s8 y$v_buf_1_SN_5)))
(assert (= y$278 (= y$n0s8 y$v_buf_1_SN_6)))
(assert (= y$280 (= y$n0s8 y$v_buf_2_NR_0)))
(assert (= y$282 (= y$n0s8 y$v_buf_2_NR_1)))
(assert (= y$284 (= y$n0s8 y$v_buf_2_NR_2)))
(assert (= y$286 (= y$n0s8 y$v_buf_2_NR_3)))
(assert (= y$288 (= y$n0s8 y$v_buf_2_NR_4)))
(assert (= y$290 (= y$n0s8 y$v_buf_2_NR_5)))
(assert (= y$292 (= y$n0s8 y$v_buf_2_NR_6)))
(assert (= y$294 (= y$n0s8 y$v_buf_2_SN_0)))
(assert (= y$296 (= y$n0s8 y$v_buf_2_SN_1)))
(assert (= y$298 (= y$n0s8 y$v_buf_2_SN_2)))
(assert (= y$300 (= y$n0s8 y$v_buf_2_SN_3)))
(assert (= y$302 (= y$n0s8 y$v_buf_2_SN_4)))
(assert (= y$304 (= y$n0s8 y$v_buf_2_SN_5)))
(assert (= y$306 (= y$n0s8 y$v_buf_2_SN_6)))
(assert (= y$308 (= y$n0s8 y$v_c)))
(assert (= y$310 (= y$n0s8 y$v_close)))
(assert (= y$312 (= y$n0s8 y$v_i)))
(assert (= y$314 (= y$n0s8 y$v_nloss)))
(assert (= y$316 (= y$n0s8 y$v_packet_element)))
(assert (= y$318 (= y$n0s8 y$v_packet_global)))
(assert (= y$320 (= y$n0s8 y$v_packet_receiver)))
(assert (= y$322 (= y$n0s8 y$v_rs_0)))
(assert (= y$324 (= y$n0s8 y$v_rs_1)))
(assert (= y$326 (= y$n0s8 y$v_rs_2)))
(assert (= y$328 (= y$n0s8 y$v_rs_3)))
(assert (= y$330 (= y$n0s8 y$v_rs_4)))
(assert (= y$332 (= y$n0s8 y$v_rs_5)))
(assert (= y$334 (= y$n0s8 y$v_rs_len)))
(assert (= y$336 (= y$n0s8 y$v_seq)))
(assert (= y$338 (= y$n0s8 y$v_sqn_global)))
(assert (= y$340 (= y$n0s8 y$v_sqn_receiver)))
(assert (= y$342 (= y$n0s8 y$v_trail_element)))
(assert (= y$344 (= y$n0s8 y$v_trail_receiver)))
(assert (= y$346 (= y$n0s8 y$v_x)))
(assert (= y$prop (not y$9304)))
(assert (= y$w$55_op (Concat_32_8_24 y$v_RN_size y$n0s24)))
(assert (= y$v3_1517448504_182_op (GrEq_1_32_32 y$w$55_op y$n7s32)))
(assert (= y$v3_1517448504_183_op (and y$a_r4 y$v3_1517448504_182_op)))
(assert (= y$id185_op (and y$111 y$v3_1517448504_183_op)))
(assert (= y$id185_op (not y$9176)))
(assert (= y$9177 (= y$prop y$9176)))
(assert (= y$9317 (and y$1 y$3 y$5 y$7 y$9 y$11 y$13 y$15 y$17 y$19 y$21 y$23 y$25 y$27 y$29 y$31 y$33 y$35 y$37 y$39 y$41 y$43 y$45 y$47 y$49 y$51 y$53 y$55 y$57 y$59 y$61 y$63 y$65 y$67 y$69 y$71 y$73 y$75 y$77 y$79 y$81 y$83 y$85 y$87 y$89 y$91 y$93 y$95 y$97 y$99 y$101 y$103 y$105 y$107 y$109 y$111 y$114 y$116 y$118 y$120 y$122 y$124 y$126 y$128 y$130 y$132 y$134 y$136 y$138 y$140 y$142 y$144 y$146 y$148 y$150 y$152 y$154 y$156 y$158 y$160 y$162 y$164 y$166 y$168 y$170 y$172 y$174 y$176 y$178 y$180 y$182 y$184 y$186 y$188 y$190 y$192 y$194 y$196 y$198 y$200 y$202 y$204 y$206 y$208 y$210 y$212 y$214 y$216 y$218 y$220 y$222 y$224 y$226 y$228 y$230 y$232 y$234 y$236 y$238 y$240 y$242 y$244 y$246 y$248 y$250 y$252 y$254 y$256 y$258 y$260 y$262 y$264 y$266 y$268 y$270 y$272 y$274 y$276 y$278 y$280 y$282 y$284 y$286 y$288 y$290 y$292 y$294 y$296 y$298 y$300 y$302 y$304 y$306 y$308 y$310 y$312 y$314 y$316 y$318 y$320 y$322 y$324 y$326 y$328 y$330 y$332 y$334 y$336 y$338 y$340 y$342 y$344 y$346 y$9304 y$9177)))
(assert y$9317)
(check-sat)
(exit)
