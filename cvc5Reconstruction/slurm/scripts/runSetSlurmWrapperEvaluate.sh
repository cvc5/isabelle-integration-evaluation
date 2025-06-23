#!/bin/bash


input_dir=$1
output_file=$2
config=$3
library=$4


if ! [ $# -eq 4 ]; then
    echo "Usage: $0 <input directory> <output file> <solver_config (cvc5_with_rewrite or cvc5_without_rewrite or verit) library>"
    exit 1
fi

echo "[" > $output_file
echo "output_file $output_file"
while read -r problem_file; do
  entry=$(cat $problem_file | grep "{")
  base_dir=${problem_file%/*/*/*}/
  outlog_file=$base_dir/output.log
  entry2=$(cat $outlog_file | grep "input_file: " | sed 's/input_file: .//g')
  raw_name=$(cat $outlog_file | grep "bench_name: ")
  
  #echo "outlog_file $outlog_file"
  #echo "problem_file: $problem_file"
  #echo "input_filew $entry2"
  #echo "raw name $raw_name"


  #this can hopefully be removed at some point
  temp="${problem_file#*/*/*/*/}"
  temp=${temp%/*/*/*}
  steps=$(grep -c "^(step" $base_dir/*.alethe)
  temp=${temp#*/}
  temp=${temp%.*}.smt2
  
  entry=$(echo $entry | sed 's|benchmark_path": "[^,]*", |benchmark_path": \"'"$entry2"'\", "library_name": \"'"$library"'\","benchmark_steps": '"$steps"', |' )
  #entry=$(echo $entry | sed 's|, "message": \(.*\),|}]},|g' )
  
  last_char="${entry: -1}"
  if ! [[ $last_char == "," ]]
  then
    if [[ $entry = *checking_time\": ]]
    then
	    entry=$entry" -1 }]},"
    else
	    entry=$entry"\" }]},"

    fi
  fi

  echo "$entry" >> $output_file
done <<< $(find "$input_dir" -type f -name "$config")

sed -i '$ s/.$//' $output_file

echo "]" >> $output_file


