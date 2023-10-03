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
      if (row[2]==' error' or row[2]==None or row[2]=='' ):
        errors.append(row)
      elif (row[1]==' evaluate))' or row[1]==' none'):
        pass
      else:
       if row[1] in time_with_lemmas_per_rule:
         time_with_lemmas_per_rule[row[1]].append(int(row[2])/1000)
       else:
         time_with_lemmas_per_rule[row[1]] = [int(row[2])/1000]
  

# Python 3.5+
labels, data = [*zip(*time_with_lemmas_per_rule.items())]  # 'transpose' items to parallel key, value lists

# or backwards compatable    
labels, data = time_with_lemmas_per_rule.keys(), time_with_lemmas_per_rule.values()

plt.boxplot(data)
plt.xticks(range(1, len(labels) + 1), labels)

plt.xlabel("Rule")
plt.ylabel("Time")
plt.title("Reconstruction time per rule")


plt.show()
