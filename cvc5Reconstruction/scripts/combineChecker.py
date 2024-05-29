import os
import json
from collections import defaultdict
import sys

directory = '/home/lachnitt/Sources/isabelle-integration-evaluation/cvc5Reconstruction/result/'
checker_directory = directory + sys.argv[1] + '/Checker/'
output_file = directory + sys.argv[1] + '/all_checking.json'


# Dictionary to store merged entries
merged_entries = {}

for filename in os.listdir(checker_directory):
    filepath = os.path.join(checker_directory, filename)

    with open(filepath, 'r') as file:
      json_data = file.read()
      
    data = json.loads(json_data)

    # Iterate over each line
    for entry in data:
      benchmark_name = entry['benchmark_name']
      # Check if the benchmark_name already exists in the merged_entries dictionary
      if benchmark_name in merged_entries:
        # Merge the 'solving' lists but only for entries that do not exist yet
        new_entries=[]
        for checkingEntry in entry['checking']:
          exists=False
          for prevEntry in merged_entries[benchmark_name]['checking']: 
            if (checkingEntry['solver_config']) == (prevEntry['solver_config']):
              exists=True
          if not exists: 
            new_entries+=[checkingEntry]
        merged_entries[benchmark_name]['checking'].extend(new_entries)
      else:
        # If benchmark_name does not exist, add the entry
        merged_entries[benchmark_name] = entry

# Convert the merged_entries dictionary back to a list of JSON strings
merged_lines = [json.dumps(value) + ',' for value in merged_entries.values()]

with open(output_file, 'w') as file:
    file.truncate(0)
    file.write('[\n')
    file.write('\n'.join(merged_lines)[:-1])
    file.write('\n]')
