import json
import pandas as pd
import sys
from statistics import median
import os

checking_input_file = sys.argv[1]
name = sys.argv[2]
#print(checking_input_file)
if not os.path.exists(checking_input_file):
  print('%s, 0, 0, 0, 0' % name)
  quit()

checking_data = pd.read_json(checking_input_file)

checking_data['checking']=(checking_data['checking'].apply(lambda x: int(x[0]['checking_time'])))
checking_data=(checking_data['checking'])

#print(checking_data)
solved=checking_data[checking_data > 1]

#TODO: eventually remove best and worst 5%
nr_total=checking_data.shape[0]
nr_success=solved.shape[0]
nr_median=round(solved.median(),2)
nr_average=round(solved.mean(),2)


print('%s, %s, %s, %s, %s' % (name,nr_total,nr_success,nr_median,nr_average))

