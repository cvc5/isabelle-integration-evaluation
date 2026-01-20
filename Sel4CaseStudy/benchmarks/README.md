Benchmarks
----------

- Lemmas from the `Word_Lib` version from L4V itself (here in folder Word_Lib):
  - Focused on the "Internal" lemmas of L4V (sel4's verification), which are the extensions to the original Word_Lib. The classification of the lemmas now is according to 3 dimensions:

    - statements of lemmas using parametric vs. concrete bv width (specifically, 32 and 64 bits)
    - statements of lemmas mixing bv with other types (e.g., through casting) vs. statements purely about bv
    - proofs that use some mechanism of instantiation of lemmas (of, where, OF) vs. proofs where they are not used.

The name of each file makes explicit to which category do its lemmas belong.
