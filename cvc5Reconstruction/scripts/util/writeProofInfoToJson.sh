#!/bin/bash
source config


if [ $# -eq 0 ]; then
    echo "Usage: $0 <output file,proof path>"
    exit 1
fi

output_file=$1
filepath=$2
proof_steps=$3
proof_file_size=$4

#proof steps, deleted lets (0=No/1=Yes/x=N/A), optional: proof file size


write_json(){
 echo '{"benchmark_name" : "'$1'", "solving": [{"solver_name" : "'$2'", "solving_time" : '$3' '$4'}]}'>> $curr_res_file
 echo ',' >> $curr_res_file
}

