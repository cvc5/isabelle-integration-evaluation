#!/usr/bin/env python3

#Mix of self written and AI

import json
import sys
import os
import shutil

verbose = False

def verbose_print(*args, **kwargs):
    if verbose:
        print(*args, **kwargs)

def load_json_file(filepath):
    try:
        with open(filepath) as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        verbose_print(f"Error: The file '{filepath}' was not found.")
        return None
    except json.JSONDecodeError as e:
        verbose_print(f"Error: Could not decode JSON from the file.\nDetails: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def copy_file(source,destination):
    try:
        shutil.copy2(source, destination)
    except shutil.SameFileError:
       verbose_print("Source and destination represent the same file.")
    except PermissionError:
       print("Permission denied.")
       sys.exit(1)
    except Exception as e:
      print(f"An error occurred: {e}")
      sys.exit(1)

def merge_files(file1, file2, outfile):
    outdir = os.path.dirname(outfile)
    if outdir:
        os.makedirs(outdir, exist_ok=True)


    # Check if the input files exist and if json data can be loaded

    exists1, exists2 = os.path.exists(file1), os.path.exists(file2)

    if not exists1 and not exists2:
        print("None of the input files was found")
        sys.exit(1)
    elif not exists1 or not exists2:
        copy_file(file2 if not exists1 else file1, outfile)
        sys.exit(0)

    data1, data2 = load_json_file(file1), load_json_file(file2)

    if data1 is None and data2 is None:
        print("Both files empty.")
        sys.exit(1)
    elif data1 is None or data2 is None:
        copy_file(file2 if data1 is None else file1, outfile)
        sys.exit(0)



    # If both files contained data merge

    merged = {}
    verbose_print("Both files contain data")
    for entry in data1 + data2:
        key = entry["benchmark_path"]
        key = os.path.normpath(key)
        if key not in merged:
            merged[key] = entry
        else:
            # merge solving arrays
            if "solving" in merged[key].keys():
              solving_entries=[s["solver_config"] for s in merged[key]["solving"]]
              solving = entry.get("solving",[])
              for s1_id, s1_entry in enumerate(entry.get("solving", [])):
                c = s1_entry.get("solver_config")
                if c not in solving_entries:
                    merged[key]["solving"].append(s1_entry)
                else:
                    merged[key]["solving"][s1_id] = s1_entry #Prefer new entry

            # merge checking arrays
            if "checking" in merged[key].keys():
              checking_entries=[s["solver_config"] for s in merged[key]["checking"]]
              checking = entry.get("checking",[])
              for s1_id, s1_entry in enumerate(entry.get("checking", [])):
                c = s1_entry.get("solver_config")
                if c not in checking_entries:
                    merged[key]["checking"].append(s1_entry)
                else:
                    merged[key]["checking"][s1_id] = s1_entry #Prefer new entry

            # keep missing fields if any
            for k, v in entry.items():
                if k not in merged[key]:
                    merged[key][k] = v


    # create / overwrite output file
    with open(outfile, "w") as f:
        json.dump(list(merged.values()), f, indent=2)

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "-v"]
    verbose = "-v" in sys.argv

    if len(args) < 3:
        print("Usage: python merge_json.py file1.json file2.json output.json [-v]")
        sys.exit(1)

    input_file1 = args[0]
    input_file2 = args[1]
    output_file = args[2]
    verbose_print(f"Merging {input_file1} and {input_file2} into {output_file}")
    merge_files(input_file1, input_file2, output_file)


#if __name__ == "__main__":
#    parser = argparse.ArgumentParser(description="Merge two .json files containing benchmark information. Supports checking and solving information")
#    parser.add_argument("input_file1", help="Path to first input file")
#    parser.add_argument("input_file2", help="Path to second input file")
#    parser.add_argument("output_file", help="Path to merged JSON file")  # no dots in argument names
#    parser.add_argument("-v", action="store_true", help="verbose mode")
#    args = parser.parse_args()
#    merge_files(args.input_file1, args.input_file2, args.output_file)

