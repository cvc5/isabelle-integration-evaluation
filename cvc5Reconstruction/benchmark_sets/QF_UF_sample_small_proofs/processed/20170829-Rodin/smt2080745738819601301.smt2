(set-info :smt-lib-version 2.6)
(set-logic QF_UF)
(set-info :source |Generator: Rodin SMT Plug-in|)
(set-info :license "https://creativecommons.org/licenses/by-nc/4.0/")
(set-info :category "industrial")
(set-info :status unsat)
(declare-fun circuit () Bool)
(declare-fun grn () Bool)
(declare-fun org () Bool)
(declare-fun rd1 () Bool)
(declare-fun rd2 () Bool)
(assert circuit)
(assert rd2)
(assert (not grn))
(assert (=> org (and (not rd1) (not rd2))))
(assert (=> rd1 (not rd2)))
(assert (not (not org)))
(check-sat)
(exit)
