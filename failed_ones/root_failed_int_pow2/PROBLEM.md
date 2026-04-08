# Matrix_Tensor int.pow2 Failure

Isolated theorem:
- `Failed_Matrix_Tensor_Length_Tensor.thy`
- theorem `length_Tensor`

Original theorem:
- `src/afp-current/afp-2026-03-22/thys/Matrix_Tensor/Matrix_Tensor.thy`
- lemma `length_Tensor`
- failing internal proof line: `595`

Original Mirabelle artifact:
- `artifacts/prob_00595_020226__41716860.smt_in`
- `artifacts/prob_00595_020226__41716860.smt_out`

Original failure:
- `Either theory is not supported or parsing instructions for the term are not included in the parser int.pow2`

```bash
./bin/isabelle build -d src/afp-current/afp-2026-03-22/thys -d root_failed_int_pow2 Root_Failed_Int_Pow2
python3 tools/analyze_output_mirabelle.py root_failed_int_pow2/artifacts --replay-selection all
```
