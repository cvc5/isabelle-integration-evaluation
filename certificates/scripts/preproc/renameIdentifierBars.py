#!/usr/bin/env python3

#Written completely by ChatGPT

import re
import argparse
import tempfile
import os
import csv

def process_file(path, pattern):
    mapping = {}
    counter = 0

    def repl(match):
        nonlocal counter
        sym = match.group(1)
        if sym not in mapping:
            mapping[sym] = f"internal_name_{counter}"
            counter += 1
        return mapping[sym]

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    result = pattern.sub(repl, text)

    dir_name = os.path.dirname(path)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=dir_name,
        delete=False
    ) as tmp:
        tmp.write(result)
        tmp_name = tmp.name

    os.replace(tmp_name, path)

def main():
    parser = argparse.ArgumentParser(
        description="Process either a directory or a CSV file of filenames"
    )
    parser.add_argument(
        "input",
        help="Directory to walk OR CSV file with <filename>[,<ignored>]"
    )
    parser.add_argument(
        "--ext",
        help="Only process files with this extension (directory mode only)",
        default=None
    )

    args = parser.parse_args()
    pattern = re.compile(r'\|([^|]+)\|')

    if os.path.isdir(args.input):
        # ----- Directory mode -----
        for root, _, files in os.walk(args.input):
            for name in files:
                if args.ext and not name.endswith(args.ext):
                    continue
                path = os.path.join(root, name)
                process_file(path, pattern)

    elif os.path.isfile(args.input):
        # ----- CSV mode -----
        with open(args.input, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue

                filename = row[0].strip()
                if not filename:
                    continue

                if not os.path.isfile(filename):
                    print(f"Skipping missing file: {filename}")
                    continue

                process_file(filename, pattern)

    else:
        parser.error(f"Input '{args.input}' is neither a directory nor a file")


if __name__ == "__main__":
    main()


