The seL4 Haskell Model
======================

The sources in this directory can be used to build a Haskell Cabal package
containing an executable model of the seL4 kernel. 

Concepts covered
----------------

- From [`seL4: Formal Verification of an Operating-System Kernel`](https://cacm.acm.org/research/sel4-formal-verification-of-an-operating-system-kernel/):
    - Reflects the fundamental restrictions in size and code structure expected from the hardware
and the C implementation.
    - The executable specification is deterministic.
    - Data structures are now explicit data types, records, and lists with straightforward, efficient implementations in C.
      - For example the capability derivation tree of seL4, modelled as a tree on the abstract level, is now modelled as a doubly linked list, manipulated explicitly with pointer-update operations.
