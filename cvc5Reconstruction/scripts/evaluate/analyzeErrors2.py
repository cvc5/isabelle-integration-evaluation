import json
import matplotlib.pyplot as plt
import sys
import numpy as np
import errorCodeUtil

#Set-up
#directory = '/home/lachnitt/Sources/isabelle-integration-evaluation/cvc5Reconstruction/'
checking_input_file = sys.argv[1] + '/all_checking.json'
bench_input_file = sys.argv[1] + '/Bench/all_bench.json'

if ((len (sys.argv)) > 2) :
  name = sys.argv[2]
else :
  name = ""


#Utils
def count_occurences(checking_entry,collect_res):
  solver_config = checking_entry.get('solver_config', None)
  checking_time = checking_entry.get('checking_time', None)
  if solver_config == 'carcara':
    if checking_time is not None:
      collect_res[checking_time] += 1
      failed_rule = checking_entry.get('failed_rule', None)
  return collect_res

def increase_category(category_dict,checking_entry,category):
  if category == -6 or category == -7:
    category_dict[abs(time)]['amount'] = category_dict.get(abs(time), 0)['amount']+1
    failed_rule = checking_entry.get('failed_rule', None)
    failed_rule_list=category_dict[abs(time)]['rules']
    if failed_rule is not None:
      failed_rule=checking_entry['failed_rule']
      if failed_rule in failed_rule_list:
        failed_rule_list[failed_rule] += 1
      else:
        failed_rule_list[failed_rule] = 1
    else:
      failed_rule_list['unknown'] += 1
    
  else:        
     category_dict[abs(category)] = category_dict.get(abs(category), 0) + 1
  return category_dict

def print_devider():
  print("--------------------------------------")

def get_percentages(pct, nr_total):
    absolute = round (pct / 100.*(nr_total))
    return "{:.1f}%\n({:d})".format(pct, int(absolute))

def mk_ax(fig,subplot_nr,data,title):
  colors=errorCodeUtil.get_colors()
  used_colors=[]
  used_data=[]
  used_labels=[]
    
  for label,d in data.items():
    if d > 0:
      used_colors.append(colors[label])
      used_data.append(d)
      used_labels.append(label)

  labels_str=[]
  for l in used_labels:
    labels_str.append(errorCodeUtil.error_codes_to_str(l))
  ax1 = fig.add_subplot(subplot_nr)
  ax1.pie(used_data, labels=labels_str, colors=used_colors, autopct=lambda pct: get_percentages(pct, sum(data.values())), startangle=140, textprops={'fontsize': 15})
  ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
  ax1.set_title(title, size=22, y=0.90,loc='center')
  
def sanitize(category_dict):
  category_dict2={0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
  for ca in category_dict:
    if ca == 6 or ca == 7:
      category_dict2[ca] = category_dict[ca]['amount']
    else:
      category_dict2[ca] = category_dict[ca]
  return category_dict2

### Main functionality

print("sdf")
# Initialize counters for different configurations:
categories_without_rewrite = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: {'amount':0,'rules':{'unknown':0}}, 7: {'amount':0,'rules':{'unknown':0}}}
categories_with_rewrite = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: {'amount':0,'rules':{'unknown':0}}, 7: {'amount':0,'rules':{'unknown':0}}}
categories_verit= {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: {'amount':0,'rules':{'unknown':0}}, 7: {'amount':0,'rules':{'unknown':0}}}

cvc5_without_rewrite='cvc5_without_rewrite'
cvc5_with_rewrite='cvc5_with_rewrite'
verit='verit'

error_categories = {
 cvc5_without_rewrite : categories_without_rewrite,
 cvc5_with_rewrite : categories_with_rewrite,
 verit : categories_verit
}    

# Read the JSON files
with open(bench_input_file, 'r') as bench_input:
  bench_input_data = json.load(bench_input)
  
if len(bench_input_data) == 0:
  print("No benchmarks found")
  exit()
  
with open(checking_input_file, 'r') as checking_input:
    checking_input_data = json.load(checking_input)

    
cvc5_without_rewrite_present = any(
  cvc5_without_rewrite in [check.get('solver_config') for check in benchmark.get('checking', [])]
  for benchmark in checking_input_data
)
cvc5_with_rewrite_present = any(
  cvc5_with_rewrite in [check.get('solver_config') for check in benchmark.get('checking', [])]
  for benchmark in checking_input_data
)
verit_present = any(
  verit in [check.get('solver_config') for check in benchmark.get('checking', [])]
  for benchmark in checking_input_data
)

subplotNrs = {cvc5_without_rewrite: 0, cvc5_with_rewrite: 0, verit: 0}
print("here")
if cvc5_without_rewrite_present and cvc5_with_rewrite_present and verit_present :
 nr_present=3
 subplotNrs = {cvc5_without_rewrite: 121, cvc5_with_rewrite: 122, verit: 123}
elif (cvc5_without_rewrite_present and cvc5_with_rewrite_present) :
 subplotNrs = {cvc5_without_rewrite: 121, cvc5_with_rewrite: 122, verit: 0}
 nr_present=2
elif (cvc5_without_rewrite_present and verit_present) :
 subplotNrs = {cvc5_without_rewrite: 121, cvc5_with_rewrite: 0, verit: 122}
 nr_present=2
elif (cvc5_with_rewrite_present and verit_present) :
 subplotNrs = {cvc5_without_rewrite: 0, cvc5_with_rewrite: 121, verit: 122}
 nr_present=2
elif cvc5_without_rewrite_present or cvc5_with_rewrite_present or verit_present :
 subplotNrs = {cvc5_without_rewrite: 121, cvc5_with_rewrite: 121, verit: 121}
 nr_present=1
else :
 exit -1

print("Found " + str(nr_present) + " solver(s)")
print_devider()

for benchmark in bench_input_data:
  benchmark_name=benchmark['benchmark_name']
  checking_benchmark_entry2=next((b for b in checking_input_data if b.get('benchmark_name') == benchmark_name), None)
  if (checking_benchmark_entry2 is not None):
    checking_benchmark_entry=checking_benchmark_entry2.get('checking')
    if checking_benchmark_entry is not None:
      for checking_entry in checking_benchmark_entry:
        time=checking_entry['checking_time']
        if time > 0:
          time=0
        category_dict=error_categories[checking_entry['solver_config']]
        increase_category(category_dict,checking_entry,time)
  


total_nr_benchmarks=len (bench_input_data)

for cat in error_categories :
  total= 0
  vals=error_categories[cat]
  for e in vals:
    if e == 6 or e == 7:
      total = total + vals[e]['amount']
    else:
      total = total + vals[e]
    
  unsolved=total_nr_benchmarks - total

  for n in range(unsolved,0,-1):
    increase_category(error_categories[cat],{},-8)


fig_success_rate = plt.figure(figsize=(20,7),dpi=144)
fig_success_rate.tight_layout(pad=15)
plt.subplots_adjust(bottom=-0.1)
plt.subplots_adjust(wspace=0.5)
plt.subplots_adjust(left=-0.005)




if cvc5_without_rewrite_present:
  print("cvc5 without rewrites")
  categories_without_rewrite_sanitized=sanitize(categories_without_rewrite)
  print(errorCodeUtil.print_error_dict(categories_without_rewrite_sanitized))
  print("Failed rules")
  print(categories_without_rewrite[6]['rules'])
  print("Timeout rules")
  print(categories_without_rewrite[7]['rules'])
  print_devider()
  ax_cvc5_without_rewrite = mk_ax(fig_success_rate,subplotNrs[cvc5_without_rewrite],categories_without_rewrite_sanitized,'cvc5 without rewrites')
  print("Median time")
  
  
  
if cvc5_with_rewrite_present:
  print("cvc5 with rewrites")
  categories_with_rewrite_sanitized=sanitize(categories_with_rewrite)
  print(errorCodeUtil.print_error_dict(categories_with_rewrite_sanitized))
  print_devider()
  ax_cvc5_with_rewrite = mk_ax(fig_success_rate,subplotNrs[cvc5_with_rewrite],categories_with_rewrite_sanitized,'cvc5 with rewrites')
  
if verit_present:
  print("verit")
  categories_verit_sanitized=sanitize(categories_verit)
  print(errorCodeUtil.print_error_dict(categories_verit_sanitized))
  print_devider()
  ax_verit = mk_ax(fig_success_rate,subplotNrs[verit],categories_verit_sanitized,'verit')
  
print("Plot categories...")
plt.suptitle(name, y=0.93, fontsize=25)
plt.show()


