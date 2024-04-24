#!/bin/bash
source config

benchmark_limit=50

verbose_mode=false
verbose_str=""

skip_pre=false
save_pre=false
save_bench=false
use_pre_image=false

solvers=""
verit=false
cvc5_with_rewrite=false
cvc5_without_rewrite=false

iterations_on=false
continue_iterate=true

stats_dir=misc

more_stats=false


usage() {
 echo "Usage: $0 [OPTIONS]"
 
 echo "Options:"
 echo " -h | --help  Display this help message"
 echo " -v | --verbose Enable verbose mode"
 
 echo "Overall options:"
 echo " -l <nr> | --batch_size <nr>  Benchmark processing batch size (default: 50)"
 echo " -t      | --additional_stats   collect additional statistics"
 
 echo "Solver options:"
 echo " -s <solver> | --solver <solver>  , with <solver> in {verit,cvc5_without_rewrite,cvc5_with_rewrite}
  solvers that should be used. Use multiple -s arguments if you want to use more than one solver"
 echo " -a          | --all  Run all available solvers"

 echo "Output options:"
 echo " -d  <dir> | --out_dir <dir> name of the directory you want to save the statistic files to (default: saved in misc)"

 echo "Process options:"
 echo " -p  | --skip_pre skip preprocessing"
 echo " -c  <dir> | --compress_bench <dir> compress and store benchmarks in directory <dir>"
 echo " -i  <dir> | --use_stored_bench <dir> Use specific image for benchmarks <dir>"
 echo " -r  | --del_timeout delete benchmarks for which at least one solver times out from preprocessed folder (helpful for having the next run without preprocessing)"
 echo " -y  <nr> | --stop <nr> stop after n iterations iterations"
 echo " -w  | --word if you want to check bv problems (deactivated by default since it takes forever to load SMT_CVC_Word). You'll also have to run the script that writes the theories again"
}

handle_options() {

#Reduce long options to short ones
for arg in "$@"; do
  shift
  case "$arg" in
    # Debug and Verbose options
    '--help')   set -- "$@" '-h'   ;;
    '--verbose')   set -- "$@" '-v'   ;;
    # Overall options
    '--batch_size') set -- "$@" '-l'   ;;
    '--additional_stats')   set -- "$@" '-t'   ;;
    # Solver options 
    '--solver') set -- "$@" '-s'   ;;
    '--all') set -- "$@" '-a'   ;;
    # Output options
    '--out_dir') set -- "$@" '-d'   ;;
    # Process options   
    '--skip_pre') set -- "$@" '-p'   ;;     
    '--compress_bench') set -- "$@" '-c'   ;;     
    '--use_stored_bench') set -- "$@" '-i'   ;;         
    '--del_timeout') set -- "$@" '-r'   ;;     
    '--stop') set -- "$@" '-y'   ;;         
    '--word') set -- "$@" '-w'   ;;
    # Other arguments
    *)          set -- "$@" "$arg" ;;
  esac
done

while getopts "hvl:s:d:atpc:b:i:ry:w" flag; do
 case $flag in
   h)
   usage
   exit 0
   ;;
   v)
   verbose_mode=true
   verbose_str="-v"
   ;;
   l)
   benchmark_limit=${OPTARG}
   ;;
   a)
   solvers=" -s cvc5_with_rewrite -s cvc5_without_rewrite -s verit"
   cvc5_without_rewrite=true;
   cvc5_with_rewrite=true;
   verit=true;
   ;;
   s)
   solvers+=" -s $OPTARG"
   if [ $OPTARG = "cvc5_without_rewrite" ]; then cvc5_without_rewrite=true;
   elif [ $OPTARG = "cvc5_with_rewrite" ]; then cvc5_with_rewrite=true;
   elif [ $OPTARG = "verit" ]; then verit=true;
   else echo "Unsupported Solver! Use one of these: verit, cvc5_without_rewrite, cvc5_with_rewrite."; exit -1; fi
   ;;
   d)
   stats_dir=("$OPTARG")
   ;;
   y)
   iterations_on=true;
   iterations=("$OPTARG")
   ;;
   t)
   more_stats=true;
   more_stats_str="-t";
   ;;
   p)
   skip_pre=true;
   ;;
   c)
   save_pre=true
   save_pre_dir_str="-c $OPTARG"
   ;;
   b)
   save_bench=true
   save_bench_dir_str="-c $OPTARG"
   ;;
   i)
   use_pre_image=true
   pre_image_dir="$OPTARG"
   ;;
   r)
   delete_timeouts_str="-r";
   ;;
   w)
   word_str="-b";
   ;;
   \?)
   usage
   exit -1
   ;;
 esac
done
}


handle_options "$@" 

echo "Make sure the base directory is set correctly!"
echo $BASE_DIR

if [ -z "$solvers" ] && [ "$use_pre_image" = false ] ; then echo "No solver set!"; exit -1; fi;

echo "Clean-up potential remains from old runs"
if ! $skip_pre ; then rm -f $PREPROC_BENCHMARK_HOME*; fi
rm -f "$Result_BENCHMARK_HOME"'cvc5_with_rewrite/*'
rm -f "$Result_BENCHMARK_HOME"'cvc5_without_rewrite/*'
rm -f "$Result_BENCHMARK_HOME"'verit/*'

echo "Set-up isabelle"
(eval "$SCRIPTS_HOME/setupIsabelle.sh $word_str")
    
    
if $skip_pre ; 
then
  echo "Skipped pre-processing"; 
else
  echo "Run pre-processing"
  (eval "$SCRIPTS_HOME/preproc.sh $verbose_str $save_pre_dir")
fi

    
echo "Populate benchmark file"
if $use_pre_image;
then
  find "$BENCHMARK_IMAGE_BENCHMARK_HOME/$pre_image_dir" -type f -name "*.smt2" > $PROBLEM_LOG
else
  ls $PREPROC_BENCHMARK_HOME > $PROBLEM_LOG
fi;

dir1="$Result_BENCHMARK_HOME"cvc5_with_rewrite
dir2="$Result_BENCHMARK_HOME"cvc5_without_rewrite 
dir3="$Result_BENCHMARK_HOME"verit

while [ -s $PROBLEM_LOG ] && [ "$continue_iterate" = "true" ] ; do
    lines=$(wc -l < $PROBLEM_LOG)
    echo "Benchmarks not tested yet: $lines. Running on next $benchmark_limit files."
    mkdir -p $dir1/
    mkdir -p $dir2/
    mkdir -p $dir3/
      
    if $use_pre_image;
    then
      # Copy the next n benchmarks. Not the best way to do this but I added this as an afterthought
      head -n $benchmark_limit "$PROBLEM_LOG" | while IFS= read -r filename; do
        file=$(basename "$filename")
	directory=$(dirname "$filename")
	parent_directory=$(basename "$directory")
	filename_without_extension="${filename%.smt2}"
	cp $filename "$Result_BENCHMARK_HOME/$parent_directory/"
	cp "$filename_without_extension.alethe" "$Result_BENCHMARK_HOME/$parent_directory/"
      done
      #Delete processed benchmarks from file
      sed -i -e 1,"$benchmark_limit"d $PROBLEM_LOG
    else
      # Create an array to hold all arguments
      args=($solvers)
      if $verbose ; then echo "Running solvers"; fi
      (eval "$SCRIPTS_HOME/getProof.sh -d $stats_dir -l $benchmark_limit $solvers $delete_timeouts_str $save_bench_dir_str $more_stats_str")
    fi;
 
    if $verbose ; then echo "Running checkers"; fi 
    (eval "$SCRIPTS_HOME/runIsabelle.sh -d $stats_dir $solvers $verbose_str")
    
    if $verbose ; then echo "Delete already tested benchmarks"; fi

    rm -r $dir1/
    rm -r $dir2/
    rm -r $dir3/
    

    if $iterations_on ;
    then
     ((iterations=iterations-1))
     if [ "$iterations" -eq "0" ]
     then
      continue_iterate=false; 
      if $verbose ; then echo "Finished iteration. $iterations left"; fi
     fi;
    fi;
   
done

if $verbose ; then echo "Finished processing all benchmarks. Your results are in $EVAL_RES/$stats_dir."; fi 

echo "Preparing evaluation"
if [ "$use_pre_image" = false ]; 
then
  python3 $SCRIPTS_HOME/combineSolver.py $stats_dir
  if $verbose ; then echo "Combined solver results into $stats_dir/all_solving.json"; fi 
fi;
python3 $SCRIPTS_HOME/combineChecker.py $stats_dir
if $verbose ; then echo "Combined checker results into $stats_dir/all_checking.json"; fi 






