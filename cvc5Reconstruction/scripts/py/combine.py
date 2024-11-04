import os
import json
from collections import defaultdict
import os
import json
from collections import defaultdict
import sys

print(sys.argv)
directory = '/home/lachnitt/Sources/isabelle-integration-evaluation/cvc5Reconstruction/result/'
solver_file = directory + sys.argv[1] + '/all_solving.json'
checker_file = directory + sys.argv[1] + '/all_checking.json'
output_file = directory + sys.argv[1] + '/all.json'

# Load the contents of the two JSON files
with open(solver_file, 'r') as file1, open(checker_file, 'r') as file2:
    data1 = [json.loads(line) for line in file1.readlines()]
    data2 = [json.loads(line) for line in file2.readlines()]

# Merge the two datasets based on the benchmark_name
merged_data = {}
for entry in data1 + data2:
    benchmark_name = entry['benchmark_name']
    if benchmark_name not in merged_data:
        merged_data[benchmark_name] = {}
    merged_data[benchmark_name].update(entry)

# Write the merged data to a new JSON file
with open(output_file, 'w') as outfile:
    for benchmark_name, data in merged_data.items():
        json.dump(data, outfile)
        outfile.write('\n')


        
        
