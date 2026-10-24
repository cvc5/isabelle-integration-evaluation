(* The check, evaluated by the Poly/ML process isa-poly.sh starts (the one
   `isabelle ML_process -l SMTCheckExternal` would start, without the JVM), in the context of
   SMTCheckExternal.SMT_Check_External (and the theories given with check.sh -t).

   It does what `check_smt` does (../ML/smt_check_external.ML, check_smt2): set up the context,
   read the two files, call SMT_Check_External.replay_only, and map the outcome to the same result
   codes (0 checked; 1 type/ML error; 2-4 term parsing; 5 problem parsing or other SMT failure;
   6 replay error; 7 timeout). Two outcomes check_smt2 does not have get their own codes:
   8 out of Poly/ML heap (check_smt2 reports it as 7), 9 an exception check_smt2 lets escape.

   The result is printed unconditionally (check_smt2 prints the long message only through
   smt_trace, which prints every goal of the proof), in two forms:
     ("RESULT_MSG", "<short message>") and ("RESULT_CODE", <code>), as check_smt2 prints them,
       for the scripts that parse smt_check's output;
     ISA_RESULT_CODE <code> and ISA_RESULT_MSG <long message>, one line each, for check.sh,
       with "memout" and "crash" in place of 8 and 9.

   The limits are optional: NONE keeps the value of the context, as smt_check does. The declare
   options, e.g. "rare_rec_mode=2, smt_nat_as_int=false", are applied last, as if by
   declare[[...]], so they override the limits. *)

fun isa_check solver problem_file proof_file smt_timeout rare_mode trace declare_options =
  let
    fun opt_put _ NONE = I
      | opt_put config (SOME v) = Config.put config v
    fun declare ctxt =
      if declare_options = "" then ctxt
      else
        let
          val srcs =
            Token.explode (Thy_Header.get_keywords' ctxt) Position.none ("[" ^ declare_options ^ "]")
            |> filter Token.is_proper
            |> Scan.read Token.stopper Parse.attribs
            |> (fn SOME srcs => srcs | NONE => error ("Bad declare options: " ^ declare_options))
          fun apply src ctxt =
            Context.proof_map (Thm.attribute_declaration (Attrib.attribute_cmd ctxt src) Drule.dummy_thm) ctxt
        in fold apply srcs ctxt end
    val lthy =
      Named_Target.theory_init (Context.the_global_context ())
      |> Local_Theory.map_contexts (K (
           opt_put SMT_Config.timeout smt_timeout
           (*the replay limits each step by smt_reconstruction_step_timeout (10 s by default), not
             by smt_timeout; a given smt_timeout is also the per-step limit, so that only the
             process's wall-clock limit applies*)
           #> opt_put SMT_Config.reconstruction_step_timeout smt_timeout
           #> opt_put SMT_Config.trace trace
           #> opt_put Alethe_Replay_RARE_Simplify_Methods.rare_rec_mode rare_mode))
    (*in replay (), so that bad declare options are reported as an error (code 1)*)
    fun make_ctxt () =
      Local_Theory.target_of lthy
      |> declare
      |> Config.put SMT_Config.check_external true
      |> SMT_Config.alethe_set_no_provided_assms true
    val problem_lines = Path.explode problem_file |> Bytes.read |> Bytes.split_lines
    val proof_lines = Path.explode proof_file |> Bytes.read |> Bytes.split_lines
    val one_line = String.translate (fn #"\n" => " " | c => String.str c)
    fun report code short msg =
      let
        val old_code = (case code of "memout" => "8" | "crash" => "9" | c => c)
      in
        if code = "0" then ()
        else writeln ("(\"RESULT_MSG\", " ^ ML_Syntax.print_string (one_line short) ^ ")");
        writeln ("(\"RESULT_CODE\", " ^ old_code ^ ")");
        writeln ("ISA_RESULT_CODE " ^ code);
        writeln ("ISA_RESULT_MSG " ^ one_line msg)
      end
    val t0 = Timing.start ()
    fun replay () =
      (SMT_Check_External.replay_only solver (make_ctxt ()) problem_lines proof_lines NONE; report "0" "" "")
      handle
        SMT_Parse_Problem.SMT_PROBLEM_PARSE msg =>
          if String.isPrefix "command not supported: " msg
          then report "5" "Unsupported SMT-LIB command" ("Unsupported SMT-LIB command in problem: " ^ msg)
          else report "5" "Error parsing SMT-LIB problem" ("Error parsing SMT-LIB problem: " ^ msg)
      | SMTLIB.PARSE (l, err) =>
          report "5" "Error parsing SMTLIB into SMTLIB Tree"
            ("Error parsing SMTLIB into SMTLIB Tree: " ^ err ^ " in line " ^ Int.toString l)
      | SMTLIB_Proof.SMTLIB_PARSE ("unknown SMT type", t) =>
          report "2" "unknown SMT type" ("unknown SMT type: " ^ SMTLIB.str_of t)
      | SMTLIB_Proof.SMTLIB_PARSE ("bad SMT term", t) =>
          report "3" "bad SMT term" ("bad SMT term: " ^ SMTLIB.str_of t)
      | SMTLIB_Proof.SMTLIB_PARSE (err, t) =>
          report "4" "Unkown error parsing SMTLIB" ("Unknown error parsing SMTLIB: " ^ err ^ SMTLIB.str_of t)
      | SMT_Failure.SMT (SMT_Failure.Replay (rule, ERROR msg)) =>
          report "6" ("Error replaying step " ^ rule) ("Error replaying step " ^ rule ^ " is: " ^ msg)
      (*Interrupt_Breakdown is Poly/ML running out of heap (ISA_MAXHEAP caps it with --maxheap), not
        a timeout, which is Timeout.TIMEOUT / Time_Out below; check_smt reports it as code 7*)
      | SMT_Failure.SMT (SMT_Failure.Replay (rule, Exn.Interrupt_Breakdown)) =>
          report "memout" ("Error replaying step" ^ rule) ("Out of memory while replaying step " ^ rule)
      | SMT_Failure.SMT (SMT_Failure.Replay (rule, exn)) =>
          report "7" ("Error replaying step " ^ rule)
            ("Error replaying step " ^ rule ^ " is: " ^ General.exnMessage exn)
      | SMT_Failure.SMT (SMT_Failure.Time_Out rule) =>
          report "7" ("Error replaying step " ^ rule) ("Timeout while reconstructing rule: " ^ rule)
      | SMT_Failure.SMT err =>
          report "5" "Unkown SMT error" ("Unknown SMT error " ^ SMT_Failure.string_of_failure err)
      | Timeout.TIMEOUT _ => report "7" "Timeout" "Timeout"
      | TYPE (msg, _, _) => report "1" "Type Error" ("Type Error " ^ msg)
      | Size => report "1" "Size" "Size"
      | ERROR msg => report "1" "Error" ("Error " ^ msg)
    (* what check_smt would let escape: captured (interrupts excepted) and reported as a crash *)
    val _ =
      (case Exn.result replay () of
        Exn.Res () => ()
      | Exn.Exn exn => report "crash" "Crash" (General.exnMessage exn))
  in writeln ("REPLAY_TIME " ^ Timing.message (Timing.result t0)) end;
