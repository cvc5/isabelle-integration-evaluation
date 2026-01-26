# Documentation

This directory contains markdown and theory files with conventions and other
documentation for the l4v repository.

## Topics

Current topics are:

- [Setup](setup.md) for doing seL4 proofs
- [Naming conventions](conventions.md) in this repository
- [Commit message](commit-messages.md) conventions in this repository
- [Proof style](Style.thy) rules for this repository
- Using [`find_theorems`](find-theorems.md) effectively
- Using [`find_consts`](find-consts.md) effectively
- [De-duplicating proofs](de-duplicating-proofs.md)
- [Compacting proofs](compacting-proofs.md)
- [Architecture Split](arch-split.md) Why and How-To:
  - Specs and proofs are split into *generic* and *arch-specific* parts.
  - For many sessions, the proofs remain duplicated between architectures.
- [Haskell Assertions](haskell-assertions.md): how to use assertions in Haskell to use information from AInvs on Haskell and C levels
- General [CRefine Notes](crefine-notes.md)
- [Debugging VCG](vcg-debugging.md) goals and failures in CRefine
- [Platform branches](platform-branches.md) -- what they are and how to update them
