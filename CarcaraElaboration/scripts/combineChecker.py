import os
import json
from collections import defaultdict
import sys

print(sys.argv)
directory = '/home/lachnitt/Sources/isabelle-integration-evaluation/CarcaraElaboration/Result/'
checker_directory = directory + sys.argv[1]
print(checker_directory)
output_file = directory + sys.argv[1] + '/all_checking.json'

# Dictionary to store merged entries
merged_entries = {}

for filename in os.listdir(checker_directory):
    filepath = os.path.join(checker_directory, filename)
    print(filepath)
    
    with open(filepath, 'r') as file:
       lines = json.loads(file.read())


    # Iterate over each line
    for line in lines:
      print(line)
      entry=line
      benchmark_name = entry['benchmark_name']
    
      # Check if the benchmark_name already exists in the merged_entries dictionary
      #TODO: Only temp
      if (benchmark_name in merged_entries) :
        print( entry['checking'])
        print(entry['checking'][0]['solver_config'])
        print(merged_entries[benchmark_name]['checking'])
        print(merged_entries[benchmark_name]['checking'][0]['solver_config'])
        if  len(merged_entries[benchmark_name]['checking']) < 2 :
          # Merge the 'checking' lists
          if entry['checking'][0]['solver_config'] != merged_entries[benchmark_name]['checking'][0]['solver_config']:
            merged_entries[benchmark_name]['checking'].extend(entry['checking'])
      else:
        # If benchmark_name does not exist, add the entry
        merged_entries[benchmark_name] = entry

# Convert the merged_entries dictionary back to a list of JSON strings
merged_lines = [json.dumps(value) for value in merged_entries.values()]

with open(output_file, 'w') as file:
    file.write('[')
    file.write('\n,'.join(merged_lines))
    file.write(']')

        
        
