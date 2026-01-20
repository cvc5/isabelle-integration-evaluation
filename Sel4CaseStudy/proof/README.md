The seL4 proofs
----------------

The folder contains the following:

* [`invariant-abstract`](proof/invariant-abstract/): invariants of the seL4 abstract specification
* [`refine`](proof/refine/): refinement between abstract and design specifications
* [`crefine`](proof/crefine/): refinement between design specification and C semantics
* [`access-control`](proof/access-control/): integrity and authority confinement proofs
* [`infoflow`](proof/infoflow/): confidentiality and intransitive non-interference proofs
* [`asmrefine`](proof/asmrefine/): Isabelle/HOL part of the seL4 binary verification
* [`drefine`](proof/drefine/): refinement between capDL and abstract specification
* [`sep-capDL`](proof/sep-capDL/): a separation logic instance on capDL
* [`capDL-api`](proof/capDL-api/): separation logic specifications of selected seL4 APIs

**TODO:** add diagram describing relation between each folder
