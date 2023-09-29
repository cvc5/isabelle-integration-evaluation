#!/usr/bin/env python3

import csv
from csv import DictReader
import matplotlib.pyplot as plt
import numpy as np 
from collections import defaultdict
  
with open('Results/FileToRewrite.txt','r') as csvfile:
  dict_reader = DictReader(csvfile)
  filename_rewrite = list(dict_reader)
  
with open('Results/ResultsWithRewrites.txt','r') as csvfile:
  dict_reader = DictReader(csvfile)
  filename_time_with_lemmas = list(dict_reader)
  
with open('Results/ResultsWithoutRewrites.txt','r') as csvfile:
  dict_reader = DictReader(csvfile)
  filename_time_without_lemmas = list(dict_reader)
 
d = defaultdict(dict)
for l in (filename_rewrite, filename_time_with_lemmas):
    for elem in l:
        d[elem['file_name']].update(elem)

l3 = d.values()


d2 = defaultdict(dict)
for l in (l3, filename_time_without_lemmas):
    for elem in l:
        d2[elem['file_name']].update(elem)

l4 = d2.values()


field_names= ['file_name', 'rule', 'timeWithLemmas','timeWithoutLemmas']


with open('Results/Results.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(l4)
