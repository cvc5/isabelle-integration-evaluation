#!/bin/bash

input_dir=$1
output_dir=$2
solver_config=$3

if [ $# -ne 3 ]; then
  echo "Arguments needed: <input_dir> <output_dir> <solving_config> "
  exit 1
fi

mkdir -p "$output_dir"
mkdir -p "$output_dir/Bench"
all_bench_file="$output_dir""/Bench/all_bench.json"
all_checking_file="$output_dir""/all_checking.json"

echo "[" > $all_bench_file 
echo "[" > $all_checking_file 

benchmark_dirs=$input_dir
for current_dir_path in $benchmark_dirs/*/ ; do
  bench_name=$(basename $current_dir_path)
  #echo "Current directory $bench_name"

  while IFS= read -r out_file; do
    line=$(cat $out_file)
    #echo $line

    if ! $(echo "$line" | grep -q "\"\.smt2") ;
    then 
      if [[ $line == *, ]]
      then
        echo $line >> $all_checking_file
      else
        echo "$line-1}]}," >> $all_checking_file
      fi
    fi
  done < <(find $current_dir_path -type f -name "$solver_config")

#  all_out_files=$(find $current_dir_path -type f -name "output.log")
#  while IFS= read -r out_file; do
#	  res="0"
#	  #echo "out_file $out_file"
#	  if [ -e $out_file ]
#	  then
#	    successfull=$(grep "(\"time" $out_file)
#	    if [[ $successfull != "" ]]
#	    then
#	      out_file_without_spaces=$(cat $out_file | tr -d '\n' )
#	      res=$(echo $out_file_without_spaces | sed -n -z 's/.*time", "\([0-9]*\).*/\1/p')
#	  
#	    else
#	      error=$(grep "exception SMT Time_Out raised" $out_file)
#	      if [[ $error != "" ]]
#	      then
#		res="-7"
#	      else
#		res="-1"
#		#echo "Current directory $bench_name"
#	      fi
#	    fi
#	    #echo "time $res"
#	    echo "{\"benchmark_name\":\"$bench_name\"}," >> $all_bench_file 
#	    echo "{\"benchmark_name\":\"$bench_name\", \"checking\": [{\"solver_config\": \"$3\", \"checking_time\": $res}]}," >> $all_checking_file
#	  fi
#  done < <(find $current_dir_path -type f -name "output.log")


done;

truncate -s-2 $all_bench_file
truncate -s-2 $all_checking_file
echo "]" >> $all_bench_file 
echo "]" >> $all_checking_file 

