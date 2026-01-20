The C Semantics of seL4
=======================

    l4v/spec/cspec/

This directory contains the entry point for the automatic translation of
the seL4 source code into Isabelle/HOL.

The C semantics of the kernel is produced by first configuring and
preprocessing the C sources for a specific platform and then parsing it into
Isabelle using the C parser in `l4v/tools/c-parser`.

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
  - mk_umm_types.py 
  - KernelInc_C.thy:
    - additional automatic proofs (extending Kernel_C.thy),
      about generated bitfield functions.
  - KernelState_C.thy  
  - Substitute.thy 
  - TypHeapLimits.thy
