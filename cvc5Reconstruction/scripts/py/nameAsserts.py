import os
import re
import shutil
import sys

def transform_assertions_in_file(file_path):
    # Create a temporary file to write transformed content
    temp_file = file_path + ".tmp"
    with open(file_path, 'r') as fin, open(temp_file, 'w') as fout:
        i=0
        for line in fin:
            line = line.strip()
            if line.startswith('(assert') and not ':named' in line:
                # Extract the assertion expression within (assert ...)
                match = re.match(r'\(assert (.*)\)', line)
                if match:
                    assertion_expr = match.group(1).strip()
                    # Construct the transformed assertion format
                    transformed_line = f'(assert (! {assertion_expr} :named a{i}))'
                    fout.write(transformed_line + '\n')
                else:
                    fout.write(line + '\n')  # If unable to match, write as is
                i=i+1
            else:
                fout.write(line + '\n')
    # Replace original file with temporary file
    shutil.move(temp_file, file_path)
    print(f"Transformed file '{file_path}' overwritten.")

def transform_assertions_in_directory(root_dir):
    # Traverse directory recursively
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.smt2'):
                file_path = os.path.join(root, file)
                transform_assertions_in_file(file_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python transform_smt2.py <directory>")
        sys.exit(1)
    
    root_dir = sys.argv[1]
    
    transform_assertions_in_directory(root_dir)
