The C Semantics of seL4
=======================

    l4v/spec/cspec/

This directory contains the entry point for the automatic translation of
the seL4 source code into Isabelle/HOL.

The C semantics of the kernel is produced by first configuring and
preprocessing the C sources for a specific platform and then parsing it into
Isabelle using the C parser in `l4v/tools/c-parser`.

Some details about the formalization
------------------------------------

- From [`seL4: Formal Verification of an Operating-System Kernel`](https://cacm.acm.org/research/sel4-formal-verification-of-an-operating-system-kernel/):
  - "The translation from C into Isabelle is correctness-critical and we take 
    great care to model the semantics of our C subset precisely and foundationally."
  - "precisely: we treat C semantics, types, and memory model as the
    C99 standard4 prescribes, for instance, with architecture-dependent word 
    size, padding of structs, type-unsafe casting of pointers, and arithmetic 
    on addresses"
  - "Foundationally means that we do not just axiomatize the behavior of C on a 
    high level, but we derive it from first principles as far as possible."
  - "We treat a very large, pragmatic subset of C99 in the verification."
  
- From [`An Overview of the Verification of the seL4 Microkernel`](https://www.semanticscholar.org/paper/An-Overview-of-the-Verification-of-the-seL-4-Stevens/40d5704de14461c6e0372354aacb164b5d8a9d32):
  - "In order to reason about the C implementation, we first have to represent the
    semantics of the C code in Isabelle/HOL."
  - Process followed: 
    - "Initially, the C memory model was formalised by Tuch..."
    - "Building thereupon, a C-to-Isabelle parser4 with the purpose of translating 
      the C code into the Simpl language was developed" (located in https://github.com/seL4/l4v/tree/master/tools/c-parser)
    - "Simpl [Sch06] is a generic Isabelle/HOL framework for reasoning about 
      semantics of imperative languages. Utilising this framework, verification of 
      general properties was made more convenient by automatically abstracting the 
      Simpl representation of the C code into a high-level proof calculus with a 
      tool called autocorres"
    - "From this representation in the theorem prover we automatically obtain 
      proof obligations that assert the safety of each pointer access to global 
      variables by using a verification condition generator."
  - About AutoCorres: "AutoCorres is a tool that assists reasoning about C programs 
    in Isabelle/HOL. In particular, it uses Norrish's C-to-Isabelle parser to parse 
    C into Isabelle, and then abstracts the result to produce a result that is 
    (hopefully) more pleasant to reason about."

Top-Level Theory
----------------

The top-level theory file for this module is `Kernel_C` for the bare
translation of seL4 into Isabelle, and `KernelInc_C` for additional automatic
proofs about generated bitfield functions.


Folders and files
-----------------

- Folders:
  - Architecture-specific content:
    - Kernel_C.thy (in the corresponding arch folder):
      - The top-level theory file.
    - Arch folders:
      - AARCH64  
      - ARM      
      - ARM_HYP  
      - RISCV64
      - X64
  - c:
  
- Files:
  - `mk_umm_types.py`: 
  - `KernelInc_C.thy`:
    - additional automatic proofs (extending the corresponding `Kernel_C.thy`),
      about generated bitfield functions.
  - `KernelState_C.thy`:
  - `Substitute.thy`:
  - `TypHeapLimits.thy`:
