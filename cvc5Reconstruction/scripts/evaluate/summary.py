import os
import json
from collections import defaultdict
import matplotlib.pyplot as plt
import sys
import pandas as pd

directory = '/home/lachnitt/Sources/isabelle-integration-evaluation/cvc5Reconstruction/result/'
input_file = directory + sys.argv[1] + '/all.json'


#Generate table like this

# Total number of benchmarks:
#
# solver               | solved | reconstructed |
# -----------------------------------------------
# cvc5_with_rewrite    |        |
# cvc5_without_rewrite |        |
# verit                |        |
#
# On benchmarks solved and reconstructed by both:
#
# solver               |  average solving time | average reconstruction time | 
# ----------------------------------------------------------------------------
# cvc5_with_rewrite    |                       |
# cvc5_without_rewrite |                       |
# verit                |                       |
#
# Later: Maybe Proof size additionally?


def count(search_str,checking_dict,current_solver_entry,current_solver_time) :
    if current_solver_entry == search_str and current_solver_time >= 0:
        current_checking_time=checking_times.get(current_solver_entry)
        if current_checking_time >=0:
            return [1,1,current_solver_time,current_checking_time]
        return [1,0,current_solver_time,0]
    return [0,0,0,0]


with open(input_file, 'r') as file:
    data = json.load(file)

measurement = ['solved', 'reconstructed','average solving time (in ms)', 'average checking time (in ms)']
cvc5_with_rewrite_data=[0,0,0,0]
cvc5_without_rewrite_data=[0,0,0,0]
verit_data=[0,0,0,0]

checking_times = {}

for entry in data:
    # Add checking times to the dictionary
    for checking_entry in entry['checking']:
        solver_config = checking_entry['solver_config']
        checking_times[solver_config] = checking_entry['checking_time']
        
    for solving_entry in entry['solving']:
    	current_solver_entry=solving_entry['solver_name']
    	current_solver_time=solving_entry['solving_time']

    	result=count('cvc5_with_rewrite',checking_times,current_solver_entry,current_solver_time)
    	cvc5_with_rewrite_data = [sum(pair) for pair in zip(cvc5_with_rewrite_data, result)]
    
    	result=count('cvc5_without_rewrite',checking_times,current_solver_entry,current_solver_time)
    	cvc5_without_rewrite_data = [sum(pair) for pair in zip(cvc5_without_rewrite_data, result)]
       
    	result=count('verit',checking_times,current_solver_entry,current_solver_time)
    	verit_data = [sum(pair) for pair in zip(verit_data, result)]
    	
checking_times.clear()

print(f"Total number of benchmarks: {len(data)}\n")

cvc5_with_rewrite_data = [round(num / cvc5_with_rewrite_data[0], 2) if idx == 2 else num for idx, num in enumerate(cvc5_with_rewrite_data)] 
cvc5_with_rewrite_data = [round(num / cvc5_with_rewrite_data[1], 2) if idx == 3 else num for idx, num in enumerate(cvc5_with_rewrite_data)] 
cvc5_without_rewrite_data = [round(num / cvc5_without_rewrite_data[0], 2) if idx == 2 else num for idx, num in enumerate(cvc5_without_rewrite_data)] 
cvc5_without_rewrite_data = [round(num / cvc5_without_rewrite_data[1], 2) if idx == 3 else num for idx, num in enumerate(cvc5_without_rewrite_data)] 
verit_data = [round(num / verit_data[0], 2) if idx == 2 else num for idx, num in enumerate(verit_data)] 
verit_data = [round(num / verit_data[1], 2) if idx == 3 else num for idx, num in enumerate(verit_data)] 

#temp:
cvc5_with_rewrite_data = [round(num / 1000000, 2) if idx == 2 else num for idx, num in enumerate(cvc5_with_rewrite_data)] 
cvc5_without_rewrite_data = [round(num / 1000000, 2) if idx == 2 else num for idx, num in enumerate(cvc5_without_rewrite_data)] 
verit_data = [round(num / 1000000, 2) if idx == 2 else num for idx, num in enumerate(verit_data)] 


table = [cvc5_with_rewrite_data,cvc5_without_rewrite_data,verit_data]
df = pd.DataFrame(table, columns = measurement, index=['cvc5_with_rewrite', 'cvc5_without_rewrite', 'verit'])

print(df)

print("\n")

for entry in measurement:
  print(f"| {entry} ",end='')
  

