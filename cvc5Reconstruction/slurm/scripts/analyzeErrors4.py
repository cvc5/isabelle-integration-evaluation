import json
import pandas as pd
import sys
from statistics import median
import os
import pathlib
import errorCodeUtil
from tabulate import tabulate
from tabulate import SEPARATING_LINE

checking_input_file = sys.argv[1]
#print(checking_input_file)
if not os.path.exists(checking_input_file):
  print("Input file does not exist")
  quit()

try:
    data = pd.read_json(checking_input_file,encoding_errors='ignore')
except ValueError as e:
    print("Invalid JSON syntax. Try python3 -mjson.tool $input_file")
    quit()

total_benchs_per_set={} #not needed but makes stuff easier
results_per_set={}
times_per_set_per_benchmark={}
failed_rule_per_set={}
failed_rule_list=[]
errors_list=[]
found_configs=[]

for i,d in data.iterrows():
    path=d['benchmark_path']
    #path=pathlib.PurePath(path) 
    #set_name=path.parent.name
    head,tail = os.path.split(os.path.normpath(path))
    set_name = d['library_name']
    if set_name not in total_benchs_per_set:
      total_benchs_per_set[set_name] = 0
    total_benchs_per_set[set_name] += 1

    if ('checking' in d.keys()) and (isinstance(d['checking'], list)):
     for c in d['checking']:
      config=c['solver_config']
      if config not in found_configs:
          found_configs.append(config)
      if config not in results_per_set:
          results_per_set[config]={}
      time=c['checking_time']
      #Initialize new set
      if set_name not in results_per_set[config]:
         results_per_set[config][set_name] = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
      if set_name not in times_per_set_per_benchmark.keys():
         times_per_set_per_benchmark[set_name]={}
      if path not in times_per_set_per_benchmark[set_name].keys():
         times_per_set_per_benchmark[set_name][path]={}

      if time > 0:
         if time > 150000:
             print("ALERT",time)
         results_per_set[config][set_name][0] += 1
         times_per_set_per_benchmark[set_name][path][config]=time
      else:
        results_per_set[config][set_name][-time] +=1
        if c['checking_time']!= -7:
          errors_list.append(path)

      if 'failed_rule' in c.keys():
        failed_rule_list.append(path)

        if config not in failed_rule_per_set.keys():
            failed_rule_per_set[config]={}
        
        failed_rule_config = failed_rule_per_set[config];
        if set_name not in failed_rule_config:
          failed_rule_config[set_name]={}
        failed_rule_set = failed_rule_config[set_name];
        failed_rule = c['failed_rule']
        if failed_rule not in failed_rule_set:
           failed_rule_set[failed_rule] = 0
        failed_rule_set[failed_rule] += 1

success_per_set={}
results_per_config={}

for config in results_per_set:
  success_per_set[config]={}
  results_per_config[config]={ 0:0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
  for bset in results_per_set[config]:
      success_per_set[config][bset] = results_per_set[config][bset][0]
      for i in results_per_set[config][bset]:
        results_per_config[config][i] += results_per_set[config][bset][i]

   #print(success_per_set)

    #TODO: eventually remove best and worst 5%
    #nr_total=checking_data.shape[0]
    #nr_success=solved.shape[0]
    #nr_median=round(solved.median(),2)
    #nr_average=round(solved.mean(),2)

nr_configs=len(found_configs)

print()
print("--------------------------------------")
print("---------------Overview---------------")
print("--------------------------------------")
print()

print("Total: ", len(data))
#print("Found the following configurations:", found_configs)
print("Successfully reconstructed by config:")
for config in results_per_config:
    print(" ",config,": ", results_per_config[config][0])


#print(results_per_set)
collect_sets=[]
configs=[]
for s in success_per_set:
    if s not in configs:
        configs.append(s)
    for b in success_per_set[s]:
        if b not in collect_sets:
            collect_sets.append(b);
#print(collect_sets)
#print(configs)

data2=[]
configs2=[]
configs2b=['','']
total_time={}
all_d=0


configs2.insert(0,'Total')
configs2.insert(0,'benchmark set')
for set_name in collect_sets:
  all_d = all_d + total_benchs_per_set[set_name]
total_success_per_config={'total':all_d}

for config in found_configs:
  total_success_per_config[config]=0
  total_time[config]=0
  configs2.append("Number Reconstructed")
  configs2b.append(config)

for config in found_configs:
  configs2.append("Average Reconstructed Time")
  configs2b.append(config)

data2.append(configs2)
data2.append(configs2b)
data2.append(SEPARATING_LINE)

nr_solved_by_all=0
nr_solved_by_none=0
for bench_set in collect_sets:
  data_entry=[bench_set,total_benchs_per_set[bench_set]]

  for config in found_configs:
    if bench_set in success_per_set[config]:
      data_entry.append(success_per_set[config][bench_set])
      total_success_per_config[config] += success_per_set[config][bench_set]
    else:
      data_entry.append(0)

  time_all_solved={}
  nr_all_solved=0
  for c2 in found_configs:
    time_all_solved[c2]=[]
  for bench_path in times_per_set_per_benchmark[bench_set]:
        if len(times_per_set_per_benchmark[bench_set][bench_path]) == nr_configs:
            nr_all_solved += 1
            nr_solved_by_all+=1
            for config in times_per_set_per_benchmark[bench_set][bench_path]:
              time_all_solved[config].append(times_per_set_per_benchmark[bench_set][bench_path][config])
        if len(times_per_set_per_benchmark[bench_set][bench_path]) == 0:
            nr_solved_by_none+=1
  for c2 in found_configs:
    if nr_all_solved == 0:
      data_entry.append('-')
    else:  
      data_entry.append(int(sum(time_all_solved[c2])/nr_all_solved))
      total_time[c2]+=sum(time_all_solved[c2])
 
  data2.append(data_entry)

total_per_config=list(total_success_per_config.values())
total_per_config.insert(0,'Total')
for config in found_configs:
  if total_success_per_config[config] == 0:
    total_per_config.append(0)
  else:
    total_per_config.append(int(total_time[config]/total_success_per_config[config]))

data2.append(SEPARATING_LINE)
data2.append(total_per_config)
for config in found_configs:
  configs.insert(0,str(config))

print("break-down:")
for config in results_per_config:
    print("  Reconstructed only by ",config,": ", results_per_config[config][0]-nr_solved_by_all)
print("  Reconstructed proofs of all:",nr_solved_by_all)
print("  Reconstructed of none:",nr_solved_by_none)
print()
print("--------------------------------------------------------------")
print("------------------ Reconstruction Success --------------------")
print("--------------------------------------------------------------")
print()


print("The Number Reconstructed shows the real number of reconstructed benchmarks. Average Reconstruction Time the total average time to reconstruct. Sanitized Time is the average taking the best and worst 5% of benchmarks out.")



print(tabulate(data2))


print()
print("--------------------------------------")
print("----------Error Distribution----------")
print("--------------------------------------")
print()

for config in results_per_config:
  print(config)
  print("--------------------")
  if len(results_per_config[config]) != 0:
    for error_cat in results_per_config[config]:
      print("  ", errorCodeUtil.error_codes_to_str(error_cat), results_per_config[config][error_cat])
  print()


print()
print("--------------------------------------")
print("----------Failed Rules----------------")
print("--------------------------------------")
print()

for config in failed_rule_per_set:
  print(config)
  print("--------------------")
  if len(failed_rule_per_set[config]) == 0:
      print("none")
  for bench_set in failed_rule_per_set[config]:
    print("  ", bench_set, failed_rule_per_set[config][bench_set])
  print()




print()    


for c in results_per_set:
    print()
    print("--------------------------------------------------------------")
    print(c)
    print("--------------------------------------------------------------")
    print()
    data3=[]
    configs3=[]

    total={}
    for r in (results_per_set[c]):
      temp=(results_per_set[c][r])
      temp2=({'set': r})
      temp3=({**temp2,**temp})
      data3.append(temp3.values())

    data3.append(SEPARATING_LINE)
    temp=(results_per_config[c])
    temp2=({'set': 'total'})
    temp3=({**temp2,**temp})
    data3.append(temp3.values())

    configs3.insert(0,'no proof')
    configs3.insert(0,'timeout')
    configs3.insert(0,'replay error')
    configs3.insert(0,'error AST')
    configs3.insert(0,'unknown SMT parsing error')
    configs3.insert(0,'unknown SMT term')
    configs3.insert(0,'unknown SMT type')
    configs3.insert(0,'general failure')
    configs3.insert(0,'success')
    configs3.insert(0,'set name')
    print(tabulate(data3,headers=configs3))

 

f = open("errors.json", "w")
f.write("")
f.close()
failed_entries = data
failed_entries['checking']=(failed_entries['checking'].apply(lambda x: x[0]))
failed_entries = failed_entries[failed_entries['checking'].apply(lambda x: int(x['checking_time'])) < 0]
failed_entries.to_json("errors.json", indent=1, orient = 'records', compression = 'infer', index = 'false')


f = open("failed_rules.txt", "w")
f.write("")
f.close()

f = open("failed_rules.txt", "a")
for b in failed_rule_list:
  f.write(b+'\n')
f.close()


f = open("errors.txt", "w")
f.write("")
f.close()

f = open("errors.txt", "a")
for b in errors_list:
  f.write(b+'\n')
f.close()


