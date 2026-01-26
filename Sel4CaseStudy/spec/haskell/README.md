The seL4 Haskell Model
======================

The sources in this directory can be used to build a Haskell Cabal package
containing an executable model of the seL4 kernel. 

Concepts covered
----------------

- From [`seL4: Formal Verification of an Operating-System Kernel`](https://cacm.acm.org/research/sel4-formal-verification-of-an-operating-system-kernel/):
    - Reflects the fundamental restrictions in size and code structure expected 
      from the hardware and the C implementation.
    - The executable specification is deterministic.
    - Data structures are now explicit data types, records, and lists with straightforward, 
      efficient implementations in C.
      - For example the capability derivation tree of seL4, modelled as a tree on 
        the abstract level, is now modelled as a doubly linked list, manipulated 
        explicitly with pointer-update operations.

- From [`An Overview of the Verification of the seL4 Microkernel`](https://www.semanticscholar.org/paper/An-Overview-of-the-Verification-of-the-seL-4-Stevens/40d5704de14461c6e0372354aacb164b5d8a9d32):
  - "[its] objective is to eliminate the nondeterminism of the abstract 
    specification by giving a concrete implementation."
  - "the executable specification is generated directly from the Haskell
    prototype using an handwritten tool" (https://github.com/seL4/l4v/tree/master/tools/haskell-translator)
  - "due to constraints of Isabelle/HOL, it is required that all Haskell functions 
    terminate. For simplicity of verification, only simple recursion patterns were 
    used in the Haskell functions. All in all, the restrictions above lead to easy, 
    often even automatic, termination proofs. As a corollary, the termination
    of all seL4 API calls directly follows."
