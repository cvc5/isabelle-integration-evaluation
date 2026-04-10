# AList Parser Failure

Isolated theorem:
- `Failed_AList_Distinct_Compose.thy`
- theorem `distinct_compose`

Original theorem:
- `src/HOL/Library/AList.thy`
- lemma `distinct_compose`
- failing internal proof line: `674`

Original Mirabelle artifact:
- `artifacts/prob_00674_022631__53733548.smt_in`
- `artifacts/prob_00674_022631__53733548.smt_out`

Original failure:
- `Unhandled exception ALETHE_PROOF_PARSE "Error parsing Alethe proof step: step_kind unrec: \"error\""`

./bin/isabelle build -d root_failed_alist Root_Failed_AList
python3 tools/analyze_output_mirabelle.py root_failed_alist/artifacts --replay-selection all
```
