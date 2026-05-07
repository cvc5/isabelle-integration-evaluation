#!/bin/bash
trap "cd \"${PWD}\"" EXIT


if ! [ $# -ge 3 ]; then
  echo "Usage: $0 <input_session_dir ABSOLUTE PATH> session_name> <output_dir> <"
  exit 1
fi

timeout=350
partition="quad"

Help()
{
   # Display Help
   echo "Run mirabelle on a session via slurm"
   echo
   echo "options:"
   echo "t     Set timeout for solving and producing proof"
   echo "p     Override partition in config"
   echo "i     Only run on files in <input_file.txt>"
   echo "h     Print this Help."
   echo
}

while getopts ":hp:t:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      p) partition=$OPTARG;;
      t) timeout=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done


#Read positional arguments
shift $((OPTIND - 1))

input_session_dir=$1
input_session_name=$2
output_dir=$3
export USER_HOME=/barrett/scratch/lachnitt/Binaries/IsabelleSetUp/

#set slurm timout
slurm_timeout=$((timeout + 100))
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

#Delete double slashes from file paths
input_session_dir="${input_session_dir//\/\//\/}"
output_dir="${output_dir//\/\//\/}"

rm -rf $output_dir/*
mkdir -p "$output_dir"
cd "$output_dir"

name="mirabelle_$input_session_name"

bench_file="benchmark_set_$input_session_name"
touch $bench_file
echo $input_session_name > $bench_file
output=$(/barrett/scratch/local/bin/submit-job.sh --partition "$partition" -t $slurm_timeout -n "$name" --full-access-dir $input_session_dir -b "$input_session_name" -d "Results/" --copy "/barrett/scratch/lachnitt/Binaries/isabelle-integration-evaluation/mirabelle/.isabelle" -o "${input_session_dir}" $SCRIPT_DIR/runMirabelle.sh)
echo $output  
