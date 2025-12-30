#!/bin/bash


input_dir=$1
output_file=$2
library=$3


if ! [ $# -eq 3 ]; then
    echo "Usage: $0 <input directory> <output file> <library>"
    exit 1
fi

echo "[" > $output_file
echo "output_file $output_file"
while read -r output_log_file; do
  echo "{" >> $output_file
  checking_str=""
  while IFS= read -r line
  do
    if [[ $line == "CONFIG"* ]]
    then
      l=${line#"CONFIG: "}
      checking_str=$checking_str"\"solver_config\": \""$l"\","
    elif [[ $line == !* ]]
    then
       l=${line#"!"}
       echo "$l," >> $output_file
    elif [[ $line == "SMT: RESULT_CODE"* ]]
    then
       l=${line#"SMT: RESULT_CODE: "}
       checking_str=$checking_str"\"checking_success\": \""$l"\","
    elif [[ $line == "SMT: RESULT_MSG:"* ]]
    then
       l=${line#"SMT: RESULT_CODE: "}
       checking_str=$checking_str"\"error_msg\": \""$l"\","
    elif [[ "$line" ==  "  total time"* ]]
    then
       l=${line#"  total time: "}
       l=${l%" ms"}
       checking_str=$checking_str"\"checking_time\":\"$l\","
    fi
  done < "$output_log_file"
 
  checking_str=${checking_str%?} #TODO: Add check that this is indeed a comma
  echo "\"checking\" : [{$checking_str}]," >> $output_file
  echo "\"library_name\": \"$library\"" >> $output_file
  #sed -i '$s/,$//' $output_file
  echo "}," >> $output_file

done <<< $(find "$input_dir" -type f -name "output.log")

sed -i '$s/,$//' $output_file

echo "]" >> $output_file


