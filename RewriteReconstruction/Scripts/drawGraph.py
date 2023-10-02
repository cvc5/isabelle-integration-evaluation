#!/usr/bin/env python3

import csv
import sys
import matplotlib.pyplot as plt
import numpy as np 
import csv
from collections import defaultdict
from pprint import pprint
  
file_name = []
rule = []
time_with_lemmas = []
time_without_lemmas = []
errors=[]

# By chatgpt
def calculate_average_by_strings(strings, integers,name):
    result_dict = {}  # Create an empty dictionary to store the sums and counts
    
    # Iterate through both lists simultaneously
    for string, integer in zip(strings, integers):
        if string in result_dict:
            result_dict[string]["sum"] += int (integer)  # Add the integer to the existing sum
            result_dict[string]["count"] += 1  # Increment the count
        else:
            result_dict[string] = {"sum":  int(integer), "count": 1}  # Initialize the sum and count for a new string
    
    # Calculate the averages and store them in a list of dictionaries
    result_data = [{"rule": key, name: value["sum"] / value["count"]} for key, value in result_dict.items()]
    
    return result_data

res_file=str(sys.argv[1])

with open(res_file,'r') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    for row in lines:
      #file_name.append(row[0]), not needed so far
      if (row[2]==' error' or row[3]==' error' or row[2]==None or row[3]==None):
        errors.append(row)
      else:
       rule.append(row[1])
       time_with_lemmas.append(row[2])
       time_without_lemmas.append(row[3])

time_with_lemmas.pop(0)
time_without_lemmas.pop(0)
rule.pop(0)

pprint(errors)
#Make list with average time for each rewrite rule
result_time_with_lemmas = calculate_average_by_strings(rule, time_with_lemmas,"withR")
result_time_without_lemmas = calculate_average_by_strings(rule, time_without_lemmas,"withoutR")

totalTime=[]
d = defaultdict(dict)
for l in (result_time_with_lemmas, result_time_without_lemmas):
    for elem in l:
        d[elem['rule']].update(elem)
        
totalTime = d.values()

print("totalTime",totalTime)      

X_axis = np.arange(len(totalTime))

plt.bar(X_axis - 0.2, [d['withR'] for d in totalTime], 0.4, label = 'With Lemmas')
plt.bar(X_axis + 0.2, [d['withoutR'] for d in totalTime], 0.4, label = 'Without Lemmas')
  
plt.xticks(X_axis, [d['rule'] for d in totalTime])
plt.xlabel("RARE rules")
plt.ylabel("Time")
plt.title("Average time reconstruction per rule")
plt.legend()
plt.show()

