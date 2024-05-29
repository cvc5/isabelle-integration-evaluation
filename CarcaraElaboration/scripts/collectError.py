import json
import matplotlib.pyplot as plt
import sys

directory = '/home/lachnitt/Sources/isabelle-integration-evaluation/CarcaraElaboration/Result/'
input_file = directory + sys.argv[1] + '/all_checking.json'
logRun = '/home/lachnitt/Sources/isabelle-integration-evaluation/CarcaraElaboration/logRun.txt'
print(input_file)
# Read the JSON file
with open(input_file, 'r') as file:
    data = json.loads(file.read())


collectErrors=[]
# Count the entries in each category
for entry in data:
  for checking_entry in entry['checking']:
   solver_config = checking_entry.get('solver_config', None)
   checking_time = checking_entry.get('checking_time', None)
   if solver_config == 'carcara':
    if checking_time is not None:
      if checking_time == -6:
        if entry['benchmark_name'].endswith("_elaborated.smt2"):
          collectErrors.append(entry['benchmark_name'].removesuffix("_elaborated.smt2")+".smt2")
        else:
          collectErrors.append(entry['benchmark_name'])
        

collectErrors2 = "".join(["/home/lachnitt/Sources/isabelle-integration-evaluation/CarcaraElaboration/Preprocessed/" + element + "\n" for element in collectErrors])

with open(logRun, 'w') as lR:
 lR.write(collectErrors2)



print(collectErrors2)

