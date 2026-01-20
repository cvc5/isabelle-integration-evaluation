Larger, self-contained proof tools
----------------------------------

The folder contains the following:

* [`asmrefine`](tools/asmrefine/): the generic Isabelle/HOL part of the binary
      verification tool
* [`c-parser`](tools/c-parser/): a parser from C into the Simpl language in Isabelle/HOL.
       Includes a C memory model.
* [`autocorres`](tools/autocorres/): an automated, proof-producing abstraction tool from
      C into higher-level Isabelle/HOL functions, based on the C parser above
* [`haskell-translator`](tools/haskell-translator/): a basic python script for converting the Haskell
      prototype of seL4 into the executable design specification in
      Isabelle/HOL.
