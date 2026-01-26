# l4v-analysis

High-level view of L4.verified source code and related documentation (taken from [`L4.verified repo`]([docs/](https://github.com/seL4/l4v)))
-----------------------------------------------------------------------------------------------------------------------------------------------

The repository is organised as follows.

 * [`docs`](docs/): documentation on conventions, style, etc.

 * [`spec`](spec/): a number of different formal specifications of seL4.

 * [`proof`](proof/): the seL4 proofs.

 * [`lib`](lib/): generic proof libraries, proof methods and tools. Among these,
   further libraries for fixed-size machine words, a formalisation of state
   monads with nondeterminism and exceptions, a generic verification condition
   generator for monads, a recursive invariant prover for these (`crunch`), an
   abstract separation logic formalisation, a prototype of the [Eisbach][6] proof
   method language, a prototype `levity` refactoring tool, and others.

 * [`tools`](tools/): larger, self-contained proof tools

 * [`misc`](misc/): miscellaneous scripts and build tools

 * [`camkes`](camkes/): an initial formalisation of the CAmkES component platform
    on seL4. Work in progress.

 * [`sys-init`](sys-init/): specification of a capDL-based, user-level system initialiser
    for seL4, with proof that the specification leads to correctly initialised
    systems.


BENCHMARKS
----------

The [`benchmarks`](benchmarks/) folder contains our selected lemmas about bitvectors.

