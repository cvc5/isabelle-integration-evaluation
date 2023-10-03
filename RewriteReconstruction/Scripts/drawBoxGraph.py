#!/usr/bin/env python3

import csv
import sys
import os
import matplotlib.pyplot as plt
import numpy as np 
import csv
from collections import defaultdict
from pprint import pprint

time_with_lemmas_per_rule = {}
time_without_lemmas_per_rule = {}
errors=[]
     
        
directory=str(sys.argv[1])

for filename in os.listdir(directory):
  f = os.path.join(directory, filename)
  # checking if it is a file
  if os.path.isfile(f):     
   with open(f,'r') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    next(lines)
    for row in lines:
      if (row[2]==' error' or row[3]==' error' or row[2]==None or row[3]==None or row[2]==''  or row[3]=='' ):
        errors.append(row)
      elif (row[1]==' evaluate))' or row[1]==' none'):
        pass
      else:
       if row[1] in time_with_lemmas_per_rule:
         time_with_lemmas_per_rule[row[1]].append(int(row[2])/1000)
       else:
         time_with_lemmas_per_rule[row[1]] = [int(row[2])/1000]
       if row[1] in time_without_lemmas_per_rule:
         time_without_lemmas_per_rule[row[1]].append(int(row[3])/1000)
       else:
         time_without_lemmas_per_rule[row[1]] = [int(row[3])/1000]

error_only_with_lemma=0
error_only_without_lemma=0
for error_line in errors:
  if(row[2]==" error" and row[3]!=" error"):
    error_only_with_lemma+= 1
  elif(row[3]==" error" and row[2]!=" error"):
    error_only_without_lemma+= 1

print("There were %2d benchmarks that only had errors when replayed with lemmas.\n and %3d that had errors when replayed without lemmas but not with." % (error_only_with_lemma, error_only_without_lemma))   # print integer value
  
#TODO: chatgpt wrote this  
resultList = list(time_with_lemmas_per_rule.items())
rules=list(time_with_lemmas_per_rule.keys())
time_with_lemmas=[time_with_lemmas_per_rule[rule] for rule in rules]
time_without_lemmas=[time_without_lemmas_per_rule[rule] for rule in rules]

data_dict = {string: (first_values, second_values) for string, first_values, second_values in zip(rules, time_with_lemmas, time_without_lemmas)}
# Extract the labels and data for plotting
labels, data = zip(*data_dict.items())

# Prepare data for plotting two box plots side by side
data = np.array(data,dtype=object)  # Convert to NumPy array for easier manipulation
n_strings = len(labels)
width = 0.35  # Width of each box

# Create a figure and axis
fig, ax = plt.subplots()

# Create box plots for both lists side by side with custom colors
box1 = ax.boxplot(data[:, 0], positions=np.arange(n_strings), widths=width, patch_artist=True)
box2 = ax.boxplot(data[:, 1], positions=np.arange(n_strings) + width, widths=width, patch_artist=True)

# Customizing box colors
for box in [box1, box2]:
    for patch in box['boxes']:
        patch.set_facecolor('blue' if box == box1 else 'yellow')

ax.set_ylim(0, 10000)
ax.set_xticks(np.arange(n_strings) + width / 2)
ax.set_xticklabels(labels)
ax.set_xlabel('Rules')
ax.set_ylabel('Time')
ax.set_title('Time to Reconstruct Rewrite Steps')
ax.legend(['With Lemmas', 'Without Lemmas'])
plt.show()

