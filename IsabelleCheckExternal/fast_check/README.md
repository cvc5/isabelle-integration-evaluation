# fast_check

The check of `../lib/Tools/smt_check` without the JVM, adapted from `alethe-isa-check`. It does not
build a scratch theory and run `isabelle process_theories`. Instead it starts Poly/ML directly
from the `SMTCheckExternal` heap and evaluates `isa-driver.ML`, which does what `check_smt2` in
`../ML/smt_check_external.ML` does. On the test pair it takes about 1 s instead of about 13 s.

    export ISABELLE_HOME=...
    fast_check/check.sh -t Complex_Main -i $(pwd)/Test/prob_00058_001891__16939944.smt2 -p $(pwd)/Test/prob_00058_001891__16939944.alethe

It takes the same options as `smt_check`: `-d -l -t -s -o -i -p`, plus an optional trailing
timeout. It prints the same `("RESULT_MSG", ...)` and `("RESULT_CODE", n)` lines, so scripts that
parse `smt_check`'s output can call it instead. It also prints one summary line,
`[cfg isabelle] rc= time= cpu= result= code= replay_s= rss_kb= replay= qd=`. The exit status is
0 if the proof was checked, 1 if not, and 2 if inputs or the set-up are missing.

Result codes are those of `check_smt2`, plus two new ones:

| code | meaning                                                      |
|------|--------------------------------------------------------------|
| 0    | checked                                                      |
| 1    | type / ML error (also: bad `-o` options)                     |
| 2–4  | term parsing (unknown type, bad term, other)                 |
| 5    | problem parsing, other SMT failure                           |
| 6    | replay error                                                 |
| 7    | timeout inside the replay                                    |
| 8    | **new**: out of Poly/ML heap (`check_smt2` reports this as 7) |
| 9    | **new**: an exception `check_smt2` lets escape               |

A wall-clock timeout (`ISA_TIMEOUT`) kills Poly/ML, and no `RESULT_CODE` is printed, as with
`timeout smt_check`.

## Files

| File                | Contents                                                                          |
|---------------------|-----------------------------------------------------------------------------------|
| `check.sh`          | The entry point. Builds the heap if it is missing, (re)captures, runs the check under a timeout, prints the result |
| `isa-driver.ML`     | The check: `check_smt2`'s context set-up, `replay_only` and result codes          |
| `isa-poly.sh`       | Starts Poly/ML from the capture, in the context of the given theories, on one ML file, with no JVM |
| `isa-poly-setup.sh` | Captures how `isabelle ML_process -l <session>` starts Poly/ML (needs the JDK)     |

The capture is stored in `$ISABELLE_HOME_USER/smt_check_poly/<session>/`. `check.sh` makes it on
the first run and makes it again whenever the session heap is newer. After changing `../ML`,
rebuild the heap (`isabelle build -b SMTCheckExternal`). The capture contains absolute paths, so
make it on the machines that run the checks (on the cluster, run one check on the head node
first, as for the heap).

## Environment

| Variable                     | Default  | Meaning                                                    |
|------------------------------|----------|------------------------------------------------------------|
| `ISABELLE_HOME`              | required | the Isabelle tree                                          |
| `ISA_TIMEOUT`                | 900      | wall-clock limit of the whole check (s); also the trailing argument |
| `ISA_SMT_TIMEOUT`            | unset    | `smt_timeout` and the per-step limit (s); unset keeps Isabelle's values, as `smt_check` does |
| `ISA_RARE_MODE`              | unset    | `rare_rec_mode`                                            |
| `ISA_TRACE`                  | unset    | `smt_trace` (prints every goal)                            |
| `ISA_MAXHEAP`                | 9000     | Poly/ML heap cap (MB), `""` for none                       |
| `ISA_REFUSE_QUICK_AND_DIRTY` | false    | `true`: refuse to check if `quick_and_dirty` is on         |
| `KEEP_WORK`                  | unset    | directory that keeps the work files (problem, proof, Isabelle output) |

## Differences from alethe-isa-check

- It uses your `ISABELLE_HOME` and the `SMTCheckExternal` session, not a prebuilt snapshot and
  heaps, and the context is `SMTCheckExternal.SMT_Check_External` (plus `-t`) instead of `Main`.
- `quick_and_dirty` is accepted, and every result line reports it as `qd=`. `ML_process` does
  not apply the session's ROOT options, so the capture has it off (`qd=false`).
- It works with both theory loaders (`Thy_Info` in older trees, `Build` in newer ones) and with both
  `Isabelle_Process.init ()` and `init_options ()` at the end of the captured command line.
- The limits default to Isabelle's own values instead of 600 s per step and `rare_rec_mode=1`.
