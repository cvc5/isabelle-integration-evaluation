import json
import sys
import os

def merge_files(file1, file2, outfile):
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
            merged[key].setdefault("solving", [])
            merged[key]["solving"].extend(entry.get("solving", []))

            # keep missing fields if any
            for k, v in entry.items():
                if k not in merged[key]:
                    merged[key][k] = v

    # ensure output directory exists (if any)
    outdir = os.path.dirname(outfile)
    if outdir:
        os.makedirs(outdir, exist_ok=True)

    # create / overwrite output file
    with open(outfile, "w") as f:
        json.dump(list(merged.values()), f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python merge_json.py file1.json file2.json output.json")
        sys.exit(1)

    merge_files(sys.argv[1], sys.argv[2], sys.argv[3])

