#!/bin/bash
trap "cd \"${PWD}\"" EXIT

config="N/A"
logic="N/A"

Help()
{
    echo "Usage: $0 <input dir> <output dir> <output file base name>"
    echo "proof will be stored in output dir. Log data will be stored in output_file_base_name.json and
    output_file_base_name.csv in the output directory"
    exit 1
}

while getopts ":hc:l:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      c) config="$OPTARG";;
      l) logic="$OPTARG";;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done
shift $((OPTIND - 1))

#if [[ "$#" -ne 3 ]]; then
#  Help
#  exit 1
#fi

input_dir=$1
output_dir=$2
output_file=$3

if ! [[ "$output_dir" =~ ^/ ]]; then
  output_dir=$(pwd)"/"$output_dir
fi

nr_logs=$(find "$input_dir" -type f -name "output.log" | wc -l)
echo "Found $nr_logs log files"
if [[ $nr_logs = "0" ]]; then
  echo "No log files found. Stopped evaluation run. Did not delete any files."
  exit -1
fi

rm -rf $output_dir
mkdir $output_dir

output_file_json=$output_dir/$output_file".json"
touch $output_file_json
echo "[" > $output_file_json
output_file_csv=$output_dir/$output_file".csv"
rm -f $output_file_csv


find "$input_dir" -type f -name "output.log" | while read -r output_log; do
#default
result_code=10
  while IFS= read -r line; do
     case "$line" in
        '("RESULT_CODE"'*)
	     result_code=$(echo "$line" | grep -oP '(?<="RESULT_CODE", )\d+')
            ;;
        '("PROOF_FILE"'*)
            proof_file=$(echo "$line" | grep -oP '"[^"]+"' | tail -1 | tr -d '"')
            ;;
        '("PROBLEM_FILE"'*)
            problem_file=$(echo "$line" | grep -oP '"[^"]+"' | tail -1 | tr -d '"')
            ;;
	 *) #echo "line $line" 
	 if [[ "$line" == *"Error replaying step"* ]]; then
     	   echo "Found"
           tmp="${line#*Error replaying step }"
      	   error_reason="${tmp%%[,)\"[:space:]]*}"
     	   error_reason=", \"error\":\""$error_reason\"
         fi

    esac
     done < "$output_log"
  #Remove leading/trailing whitespace just in case
  logic=$(echo $logic | xargs)
  config=$(echo $config | xargs)
  echo "{\"benchmark_path\": \"$problem_file\", \"library_name\": \"$logic\", \"checking\":[{\"solver_config\": \"$config\", \"checking_outcome\": \"$result_code\"$error_reason}]}," >> $output_file_json

done

#Check last character
sed -i '$s/,$//' "$output_file_json"
echo "]" >> $output_file_json

#delete all proof files
