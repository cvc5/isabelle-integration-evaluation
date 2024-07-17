import os
import json
from collections import defaultdict
import sys

directory = '/home/lachnitt/Sources/isabelle-integration-evaluation/cvc5Reconstruction/result/'
checker_file = directory + sys.argv[1] + '/all_checking.json'
error_file = directory + sys.argv[1] + '/error_checking.json'
solver_config = "cvc5_without_rewrite"

all_errors=True
specific_error_code=-1


# Dictionary to store errors
errors_entries = {}

with open(checker_file, 'r') as file:
  json_data = file.read()
      
  data = json.loads(json_data)

  # Iterate over each line
  for entry in data:
    benchmark_name = entry['benchmark_name']
    # Check if the benchmark_name does not already exists in the errors_entries dictionary
    if benchmark_name not in errors_entries:
      for checking_entry in entry['checking']:
        solver_config = checking_entry.get('solver_config', None)
        checking_time = checking_entry.get('checking_time', None)
      
        if solver_config == 'cvc5_without_rewrite':
          if checking_time < 0:
            print(benchmark_name)
            print(checking_entry)
            errors_entries[benchmark_name] = checking_entry
            break;
         

with open(error_file, 'w') as file:
    file.truncate(0)
    file.write('[\n')
    file.write('\n'.join(errors_entries)[:-1])
    file.write('\n]')
