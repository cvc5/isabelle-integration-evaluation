#!/usr/bin/env python3

import json
import sys
import os
import shutil

def merge_files(file1, file2, outfile):
 
    # ensure output directory exists (if any)
    outdir = os.path.dirname(outfile)
    if outdir:
        os.makedirs(outdir, exist_ok=True)

    if not os.path.exists(file1) and not os.path.exists(file2):
      print("None of the input files was found")
      sys.exit(1)
    elif not os.path.exists(file1):
      if not os.path.exists(outfile):
        with open(outfile, 'w') as file:
          file.write("")
      shutil.copy2(file2, outfile)
      sys.exit(0)
    elif not os.path.exists(file2):
      if not os.path.exists(outfile):
        with open(outfile, 'w') as file:
          file.write("")
      shutil.copy2(file1, outfile)
      sys.exit(0)



    with open(file1) as f:
        data1 = json.load(f)

    with open(file2) as f:
        data2 = json.load(f)

    merged = {}

    for entry in data1 + data2:
        key = entry["benchmark_path"]
        if key not in merged:
            merged[key] = entry
        else:
            # merge solving arrays
            merged[key]["solving"].extend(entry.get("solving", []))
            # merge checking arrays
            merged[key].setdefault("checking", [])
            merged[key]["checking"].extend(entry.get("checking", []))


            # keep missing fields if any
            for k, v in entry.items():
                if k not in merged[key]:
                    merged[key][k] = v


    # create / overwrite output file
    with open(outfile, "w") as f:
        json.dump(list(merged.values()), f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python merge_json.py file1.json file2.json output.json")
        sys.exit(1)

    merge_files(sys.argv[1], sys.argv[2], sys.argv[3])

