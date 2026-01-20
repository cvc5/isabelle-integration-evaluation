The Abstract Specification of seL4
==================================

This directory contains the main Isabelle sources of the seL4 abstract
specification. The specification draws in additional interface files from
`design` and `machine`.

Concepts covered
----------------

- From [`seL4: Formal Verification of an Operating-System Kernel`](https://cacm.acm.org/research/sel4-formal-verification-of-an-operating-system-kernel/):
  - Essential concepts specified:
    - Argument formats
    - Encodings
    - Error reporting
    - Finite machine words
    - Memory
    - Typed pointers
  - Uses high-level data-structures: sets, lists, trees, functions, and records.
  - Makes use of nondeterminism in order to leave implementation choices to lower levels.

Entry Points
------------

Two useful entry points for browsing the abstract specification are the
theories `Structures_A` and `ARM_Structs_A`. They define the state space
of the kernel model, including what capabilities and kernel objects are.

The theories `Invocations_A` and `ArchInvocation_A` define datatypes for
the capability invocations/operations the kernel understands.

Most theories are named after the subsystem of the kernel they specify.

Theory files and folders
------------------------

Folders:
- Architectures-specific theories:
  - AARCH64
  - ARM
  - ARM_HYP
  - RISCV64
  - X64

Theory files (we describe only those of interest for our benchmarks):
- CSpaceAcc_A.thy
- CSpace_A.thy         
- CapRights_A.thy      
- Decode_A.thy         
- Deterministic_A.thy  
- ExceptionTypes_A.thy    
- Exceptions_A.thy        
- Glossary_Doc.thy        
- Interrupt_A.thy         
- Intro_Doc.thy    
- InvocationLabels_A.thy  
- Invocations_A.thy       
- IpcCancel_A.thy    
- Ipc_A.thy          
- KHeap_A.thy        
- KernelInit_A.thy:
  - "is a paused project and not currently included in the rest of the specification."
- MiscMachine_A.thy  
- Retype_A.thy       
- Schedule_A.thy     
- Structures_A.thy:
  - useful entry point for browsing the abstract specification
- Syscall_A.thy:
  - The top-level theory file that draws the whole specification together is `Syscall_A`, the top-level function in that theory is `call_kernel`.
- TcbAcc_A.thy
- Tcb_A.thy
- VMRights_A.thy
