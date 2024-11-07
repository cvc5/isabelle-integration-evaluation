import os
import json
from collections import defaultdict
import sys

in_checking_file = sys.argv[1]
out_checking_file = sys.argv[2]

if not os.path.exists(in_checking_file):
 print("File does not exist")
 sys.exit()
    
with open(in_checking_file, 'r') as file:
  json_data = file.read()

data = json.loads(json_data)    
new_data = []
      

# Iterate over the keys in `data` and add them to `new_data`, omitting "details"
for entry in data:
  new_entry={}
  for key in entry:
    if key == "checking":
      new_checking_entry=[]
      for checking_entry in entry[key]:
        new_checking_config={}
        for checking_config in checking_entry:
          if checking_config == "detail":
            print("skip detail")
          else:
            new_checking_config[checking_config] = checking_entry[checking_config]
        new_checking_entry.append(new_checking_config)
      new_entry[key]=new_checking_entry
    else:
      new_entry[key]=entry[key]
    print(new_entry)
    new_data.append(new_entry)

with open(out_checking_file, 'w') as out_file:
    json.dump(new_data, out_file, indent=1)

