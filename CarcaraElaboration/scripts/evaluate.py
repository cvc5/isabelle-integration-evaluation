import os
import json
from collections import defaultdict
import matplotlib.pyplot as plt
import sys

print(sys.argv)
directory = '/home/lachnitt/Sources/isabelle-integration-evaluation/CarcaraElaboration/Result/'
input_file = directory + sys.argv[1] + '/all_checking.json'


# Load the JSON data
with open(input_file, 'r') as file:
    data = [json.loads(line) for line in file]

# Filter the data 
nr_with_error = sum(1 for entry in data for checking in entry.get('checking', []) if checking.get('solver_config') == 'carcaraElab' and checking.get('checking_time') <= -1)
nr_without_error = sum(1 for entry in data for checking in entry.get('checking', []) if checking.get('solver_config') == 'carcaraElab' and checking.get('checking_time') >= 0)

# Calculate the percentage
total_benchmarks = len(data)

#These are wrong since there is duplicate data, not used for now
per_with_error = (nr_with_error / total_benchmarks)
per_without_error = (nr_without_error / total_benchmarks)

print('Of ' + str(total_benchmarks) + ' total benchmarks in ' + sys.argv[1] + ', ' + str(nr_with_error) + ' reconstructed with errors and ' + str(nr_without_error) + ' without errors')
print('That is ' + f"{per_with_error:.0%}" + ' reconstructed with errors and ' + f"{per_without_error:.0%}" + ' without errors')
