import json
import pandas as pd
import sys
import os
from pathlib import Path

def readError(input_file):
  checking_data = pd.read_json(input_file)
  for i,c in checking_data.iterrows():
      for e in c['checking']:
          error=e['checking_time']
          if (error ==-2):
              print("unknown type",c['benchmark_name'])
          elif (error == -3):
              print("unknown term",c['benchmark_name'])
          elif (error == -4):
              print("unknown parsing",c['benchmark_name'])
          elif (error == -5):
              print("unknown ast",c['benchmark_name'])
          elif (error == -6):
              if ('failed_rule' in e.keys()):
                if (e['failed_rule'] != "hole"):
                    print("replay error (non-hole)",c['benchmark_name'],e)

if __name__ == "__main__":
    readError(sys.argv[1])

