#!/bin/bash

INPUT_DIR="${1:-.}"
OUTPUT_FILE="${2:-benchmarks.json}"

# Normalize INPUT_DIR: remove trailing slashes
INPUT_DIR="${INPUT_DIR%/}"

# library_name is the last component of INPUT_DIR
# (since INPUT_DIR ends at <lib_name>/<lib_name>)
library_name=$(basename "$INPUT_DIR")

echo "[" > "$OUTPUT_FILE"

first=true
while IFS= read -r filepath; do
    benchmark_name=$(basename "$filepath")

    # Strip the INPUT_DIR prefix to get the relative portion
    # Expected structure under INPUT_DIR: <set_name>/.../<benchmark_name>
    rel="${filepath#${INPUT_DIR}/}"

    # set_name is the first directory component
    set_name=$(echo "$rel" | cut -d'/' -f1)

    # relative_benchmark_path: everything under INPUT_DIR, with leading /
    relative_benchmark_path="/${rel}"

    if [ "$first" = true ]; then
        first=false
    else
        echo "," >> "$OUTPUT_FILE"
    fi

    cat >> "$OUTPUT_FILE" <<EOF
  {
    "benchmark_name": "${benchmark_name}",
    "benchmark_path": "${filepath}",
    "relative_benchmark_path": "${relative_benchmark_path}",
    "library_name": "${library_name}",
    "set_name": "${set_name}"
  }
EOF
done < <(find "$INPUT_DIR" -type f -name "*.smt2" | sort)

echo "]" >> "$OUTPUT_FILE"

echo "Done. Output written to $OUTPUT_FILE"
