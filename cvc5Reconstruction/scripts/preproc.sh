#!/bin/bash

source config

timeout_sec=1
timeout_proof_sec=5
run_verit=false
delete_lets=true
verbose_mode=false
save_pre_image=false
limit_amount=false
delete_bench=false
small_proofs=true
nr_too_big_cvc5=0
benchmark_folder=$INPUT_BENCHMARK_HOME
output_folder=$INPUT_BENCHMARK_HOME
output_file_bench_list=$output_folder/bench.txt
output_file_results=$output_folder/bench.txt

cvc5_proof_options="--proof-format-mode=alethe --dump-proofs --produce-proofs --proof-alethe-define-skolems --full-saturate-quant --no-stats --sat-random-seed=1 --lang=smt2"
cvc5_options="--no-stats --sat-random-seed=1 --lang=smt2"
verit_options="--disable-banner -s" #TODO: How to disable proofs?
verit_proof_options="--proof-prune --proof-merge --proof-define-skolems --disable-banner -s"


debug=false

usage() {
 echo "Usage: $0 [OPTIONS]"
 echo "Options:"
 echo " -h       | --help            Display this help message"
 echo " -v       | --verbose         Enable verbose mode"
 echo " -t <nr>  | --timeout <nr>    Change timeout limit (default: 2s)"
 echo " -i       | --in		     Input folder (default: input)"
 echo " -o       | --out	     Output folder (default: output)" 
 echo " -l <nr>  | --limit <nr>      Only preprocess <nr> benchmarks and then stop (default: all are run). Note that already preprocessed benchmarks are not deleted!"
 echo " -d       | --delete_bench    This deletes sat preprocessed benchmarks from /input. Default: false"
 echo " -s       | --no_verit        Don't run verit (default: false, i.e. veriT is run)"
 echo " -n       | --no_let          Don't delete lets (default: false, i.e. lets are not deleted)"
 echo " -c <dir> | --compress <dir>  compress and store preprocessed benchmarks in directory"
}

handle_options() {

#Reduce long options to short ones
for arg in "$@"; do
  shift
  case "$arg" in
    '--help')   set -- "$@" '-h'   ;;
    '--verbose')   set -- "$@" '-v'   ;;
    '--timeout')   set -- "$@" '-t'   ;;
    '--in')   set -- "$@" '-i'   ;;
    '--out')   set -- "$@" '-o'   ;;
    '--limit')   set -- "$@" '-l'   ;;
    '--delete_bench')   set -- "$@" '-d'   ;;
    '--no_verit')   set -- "$@" '-s'   ;;    
    '--no_let')   set -- "$@" '-n'   ;;
    '--compress')   set -- "$@" '-c'   ;;  
    *)          set -- "$@" "$arg" ;;
  esac
done

while getopts "hvsl:i:o:t:c:nd" flag; do

 case $flag in
   h)
   usage
   exit 0
   ;;
   v)
   verbose_mode=true
   ;;
   s)
   run_verit=false
   ;;
   i)
   benchmark_folder=${OPTARG}
   ;;
   o)
   output_folder=${OPTARG}
   ;;
   n)
   delete_lets=false
   ;;
   l)
   limit_amount=true
   run_amount=${OPTARG}
   limit=$run_amount
   ;;
   t)
   timeout_sec=${OPTARG}
   ;;
   d)
   delete_bench=true
   ;;
   c)
   save_pre_image=true
   pre_image_name=${OPTARG}
   ;;
   \?)
   usage
   exit -1
   ;;
 esac
done
}

verbose_msg() {
  if [ "$verbose_mode" = true ] ; then echo $1; fi
}

debug_msg() {
  if [ "$debug" = true ] ; then echo $1; fi
}

delete_file(){
  file=$1
  if [ $delete_bench ] && [ -f "$file" ] ;
  then
    rm $file;
  fi;
}

declare -A solverResults

init_Result_Array() {
  solverResults=$1
  solverResults[nr_viable]=0
  solverResults[nr_unsupp]=0
  solverResults[nr_delete_let]=0
  solverResults[nr_sat]=0
  
  solverResults[nr_unknown_cvc5]=0
  solverResults[nr_error_cvc5]=0
  solverResults[nr_proof_error_cvc5]=0
  solverResults[nr_too_big_cvc5]=0
  solverResults[nr_carcara_error_cvc5]=0
  
  solverResults[nr_unknown_verit]=0
  solverResults[nr_error_verit]=0
  solverResults[nr_proof_error_verit]=0
  solverResults[nr_too_big_verit]=0
  solverResults[nr_carcara_error_verit]=0

  solverResults[curr_nr_files]=0
}

increase_Result() {
  cat=$1
  solverResults[$cat]=$((${solverResults[$cat]}+1));
}

containsUnsupportedCommand() {

grep -q -e "(define-fun" -e "(declare-datatype" -e "(declare-datatypes" -e "define-fun-rec" -e "define-fun-recs" -e "define-sort" -e "get-model" -e "pop" -e "push" -e "reset" -e "reset-assertions" $file

}

res_text=""
mk_result_str() {
 dir=$1
 nr_files=$2
 remaining1=$(($nr_files-${solverResults[nr_sat]}-${solverResults[nr_unsupp]}-${solverResults[nr_delete_let]}));
 remaining_cvc5=$(($remaining1-${solverResults[nr_error_cvc5]}-${solverResults[nr_proof_error_cvc5]}-${solverResults[nr_too_big_cvc5]}-${solverResults[nr_carcara_error_cvc5]}));
 remaining_verit=$(($remaining1-${solverResults[nr_error_verit]}-${solverResults[nr_proof_error_verit]}-${solverResults[nr_too_big_verit]}-${solverResults[nr_carcara_error_verit]}));
 res_text="
Directory: $dir


files found                    $nr_files
------------------------------------
sat                          - ${solverResults[nr_sat]}
unsupported SMT-LIB command  - ${solverResults[nr_unsupp]}
lets cannot be deleted       - ${solverResults[nr_delete_let]}
------------------------------------
remaining 		       $remaining1


                          cvc5               veriT
total	 		  $remaining1            $remaining1
-------------------------------------------
solver error            - ${solverResults[nr_error_cvc5]}  		- ${solverResults[nr_error_verit]}
proof error/timeout     - ${solverResults[nr_proof_error_cvc5]}		- ${solverResults[nr_proof_error_verit]}
proof too big:          - ${solverResults[nr_too_big_cvc5]}     	- ${solverResults[nr_too_big_verit]}
carcara error:          - ${solverResults[nr_carcara_error_cvc5]}     	- ${solverResults[nr_carcara_error_verit]}
-------------------------------------------
remaining                 $remaining_cvc5            $remaining_verit

total viable  ${solverResults[nr_viable]}"

}

write_result() {
  mk_result_str $1 $2 
  echo "$res_text"
}

write_result_to_file() {
 mk_result_str $1 $2 
  echo "$res_text" >> "$INPUT_BENCHMARK_HOME/Result.txt"
}

check_with_carcara() {
problem=$1
proof=$2
($CARCARA_HOME "check" "--ignore-unknown-rules" "$proof" "$problem" 1>/dev/null)
return $?
}


runVeriT() {
  problem=$1
  proof="${problem%.*}".alethe
  verit=$(timeout $timeout_proof_sec $VERIT_HOME $verit_options "--proof=-" "-s" "$problem")
  if [[ $? -ne 124 ]] ;
  then

    if [[ $cvc5 = "sat"* ]] ;
    then
      increase_Result "nr_sat"
      delete_file $file
    elif [[ $verit = "unsat"* ]] ;
    then
      if [[ $small_proofs ]] && [[ $(echo "$verit" | wc -l) -ge $max_nr_lines ]] ;
      then
        increase_Result "nr_too_big_verit"
      else
      	echo "$verit" > $file"_verit.alethe"
      	sed -i -e "1d" $file"_verit.alethe"
      	check_with_carcara $file $file"_verit.alethe"
      	if [[ $? -ne 0 ]]
      	then
      	  rm $file"_verit.alethe"
	  increase_Result "nr_carcara_error_verit"
	else
      	  rm $file"_verit.alethe"
          return 0
        fi;
      fi;
    else
      increase_Result "nr_error_verit"
    fi;
  else
    increase_Result "nr_error_verit"
  fi;
  return 2
}

run_cvc5()
{
  file=$1
  cvc5=$(timeout $timeout_sec $CVC5_HOME $cvc5_options $cvc5_new_problem 2>/dev/null)
  if [[ $? -ne 124 ]] ;
  then
    if [[ $cvc5 = "unkown"* ]] ;
    then
      increase_Result "nr_unknown_cvc5"
    elif [[ $cvc5 = "sat"* ]] ;
    then
      increase_Result "nr_sat"
      delete_file $file
      return 1
    else
      cvc5_proof="$(timeout $timeout_proof_sec $CVC5_HOME $cvc5_proof_options $file 2>&1)"
      return_value=$?
      max_nr_lines=1500
      if [[ $return_value = 124 ]] ; 
      then 
        debug_msg "Proof timeout"
        increase_Result "nr_proof_error_cvc5"
      elif [[ $return_value = 1 ]] ;
      then 
        debug_msg "cvc5 could not solve problem in time limit when producing proofs!"
        increase_Result "nr_proof_error_cvc5"
      elif [[ $cvc5_proof == *"error "* ]] ; #I guess this could backfire if variables have error in their name
      then 
        debug_msg "cvc5 could not solve problem! Some error occurred"
        increase_Result "nr_proof_error_cvc5"
      elif [[ $small_proofs ]] && [[ $(echo "$cvc5" | wc -l) -ge $max_nr_lines ]] ;
      then
        increase_Result "nr_too_big_cvc5"
      else
      	echo "$cvc5_proof" > $file"_cvc5.alethe"
      	sed -i -e "1d" $file"_cvc5.alethe"
      	check_with_carcara $file $file"_cvc5.alethe"
      	if [[ $? -ne 0 ]]
      	then
	  rm $file"_cvc5.alethe"
	  increase_Result "nr_carcara_error_cvc5"
	else
	  rm $file"_cvc5.alethe"
          return 0
        fi;
      fi;
    fi;
  else
    increase_Result "nr_error_cvc5"
  fi;
  return 2
}




# Main

handle_options "$@" 

benchmark_set_name=()
benchmark_nr_successfull=()
benchmark_nr=()
benchmark_nr_too_big_cvc5=()
echo "" > $output_file_bench_list
echo "" > $output_file_results


for current_dir_path in $benchmark_folder/*/ ; do

  # find benchmarks
  current_dir=$(basename "$current_dir_path")
  echo "Current directory $current_dir"
  benchmark_set_name+=("$current_dir")
  nr_files=$(find "$current_dir_path" -type f -name "*.smt2" | wc -l);
  init_Result_Array
  curr_nr_files=0

  while read -r file; do

    diff=$(($nr_files - $curr_nr_files))
    verbose_msg "Nr files left: $diff"
    curr_nr_files=$(($curr_nr_files + 1));
    debug_msg "Preprocess file: $file"
    viable_str="viable: false" 
	  
    if grep -q "(set-info :status sat)" "$file"  ;
    then
      debug_msg "benchmark has info that it is sat"
      delete_file $file
      increase_Result "nr_sat"
    elif containsUnsupportedCommand $file;
    then
      debug_msg "benchmark has command not supported"    
      delete_file $file
      increase_Result "nr_unsupp"
    else
      cvc5_new_problem=$(timeout $timeout_sec $CVC5_HOME -o raw-benchmark --parse-only --dag-thres=0 "$file" 2>/dev/null)
      ret=$?
      if [[ $ret = 124 ]]
      then
        debug_msg "lets could not be deleted from proof (timeout)"
        increase_Result "nr_delete_let"
        delete_file $file
      elif [[ $ret = 1 ]]
      then
        debug_msg "lets could not be deleted from proof (error)"
        increase_Result "nr_delete_let"
        delete_file $file
      else
        echo "$cvc5_new_problem" > "$file"
        run_cvc5 "$file"
        ret=$?
        viable=false
        
        if [[ $ret = 0 ]]
        then
          viable=true
        fi;

        if [[ $ret -ne 1 ]] #benchmark is sat
      	then
          if ! $run_verit 
  	  then 
  	    runVeriT $file
	    if [[ $? = 0 ]]
            then
              viable=true
            fi;
  	  fi;
  	fi;

        if $viable
        then
	  increase_Result "nr_viable"
	  echo "$file" >> $PROOF_OKAY_LOG
	  viable_str="viable: true"
	else
	  delete_file $file #TODO: Separate option?
        fi;
      fi;
      $SCRIPTS_HOME/util/writeGeneralBenchInfoToJson.sh 	    $output_file_bench_list $(basename $file) $file false "$viable_str"
    fi;

  if $limit_amount ; 
  then 
    run_amount=$(($run_amount-1));
    if [[ $run_amount = 0 ]] ;
    then break;
    fi;
  fi;
  done <<< $(find $current_dir_path -type f -name "*.smt2")


  if $delete_bench 
  then verbose_msg "I deleted all files I preprocessed"; 
  else verbose_msg "I did not delete the files I preprocessed"; 
  fi;

  if $run_verit 
  then verbose_msg "I ran veriT"; 
  else verbose_msg "I did not run veriT"; 
  fi;

 benchmark_nr_successfull+=("$nr_viable")
 benchmark_nr_too_big_cvc5+=("$nr_too_big_cvc5")
 benchmark_nr+=("$nr_files")
 echo ""
 write_result $current_dir $nr_files 
 write_result_to_file $current_dir $nr_files  $nr_unsupp
 echo ""
 echo ""

 if [[ $run_amount = 0 ]];
 then
   echo "I might not have processed all benchmarks in that directory"; break; 
 fi;
done    

echo ""
i=0
for dir in "${benchmark_set_name[@]}"
do
   echo "Directory: $dir" >> "$INPUT_BENCHMARK_HOME/Result.txt"
   echo "Nr files found: ${benchmark_nr[$i]}" >> "$INPUT_BENCHMARK_HOME/Result.txt" 
   echo "Nr files viable: ${benchmark_nr_successfull[$i]}" >> "$INPUT_BENCHMARK_HOME/Result.txt"
   echo "Nr of these files too big proof: ${benchmark_nr_too_big_cvc5[$i]}" >> "$INPUT_BENCHMARK_HOME/Result.txt"
   echo ""
   i=$(($i+1));
done

