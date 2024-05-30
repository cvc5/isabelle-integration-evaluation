import os
import json
from collections import defaultdict
import sys

error_directory = '/home/lachnitt/Sources/isabelle-integration-evaluation/cvc5Reconstruction/data/'
print("save_error.py")
solver=sys.argv[1]
print(solver)
output = open("/home/lachnitt/Sources/isabelle-integration-evaluation/cvc5Reconstruction/data/errors.txt", "a")   
 

checker_file = error_directory + 'curr_check_' + solver + '.txt'

 
# Dictionary to store merged entries merged_entries = {}

with open(checker_file, 'r') as file:
 json_data = file.read()
 data = json.loads(json_data)      
    
# Iterate over each line
for entry in data:

    for checking_entry in entry['checking']:
      solver_config = checking_entry.get('solver_config', None)
      checking_time = checking_entry.get('checking_time', None)
      if solver_config == solver:
        if checking_time is not None:
          if checking_time < 0:
           output.write(solver + '/' + entry['benchmark_name'] + '\n')
          if checking_time > 0:
           os.remove("/home/lachnitt/Sources/isabelle-integration-evaluation/cvc5Reconstruction/data/preprocessed/" + entry['benchmark_name'])

