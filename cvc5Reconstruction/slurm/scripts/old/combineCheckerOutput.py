import json
import pandas as pd
import sys
import os
from pathlib import Path

def combine(input_directory):
    merged=pd.DataFrame()
    error=pd.DataFrame()
    for root, dirs,_ in os.walk(input_directory):
        for d in dirs:
            f=Path(os.path.join(root,os.path.join(d,"all_checking.json")))
            if f.is_file():
                print("found",f)
                checking_data = pd.read_json(f)
                merged=pd.concat([merged,checking_data])
                for i,c in checking_data.iterrows():
                  include=False
                  for e in c['checking']:
                      if (e['checking_time']) < 0:
                        include=True
                        #if (e['checking_time'] <= -2) and (e['checking_time'] >= -6):
                        #  if ('failed_rule' in e.keys()):
                        #      if (e['failed_rule'] != "hole"):
                        #          print(c)
                  if include:
                     error=pd.concat([error,checking_data])
                     checking_data.to_json(Path(root + "/error_checking.json"), indent=1, orient = 'records', compression = 'infer', index = 'false')    

    merged.to_json(Path(input_directory + "/all_checking.json"), indent=1, orient = 'records', compression = 'infer', index = 'false')    

    error.to_json(Path(input_directory + "/error_checking.json"), indent=1, orient = 'records', compression = 'infer', index = 'false')    

if __name__ == "__main__":
    combine(sys.argv[1])

