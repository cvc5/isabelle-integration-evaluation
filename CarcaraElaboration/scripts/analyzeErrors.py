import json
import matplotlib.pyplot as plt
import sys

directory = '/home/lachnitt/Sources/isabelle-integration-evaluation/CarcaraElaboration/Result/'
input_file = directory + sys.argv[1] + '/all_checking.json'
print(input_file)
# Read the JSON file
with open(input_file, 'r') as file:
    data = json.loads(file.read())

verit_res = {
    'success': 0,
    'unknown error': 0,
    'unknown SMT type': 0,
    'unknown SMT term': 0,
    'error parsing SMT-LIB': 0,
    'error parsing outer SMT-LIB': 0,
    'Failure to replay': 0,
    'not solved' : 0,
    'timeout' : 0
}

verit_elab_res = {
    'success': 0,
    'unknown error': 0,
    'unknown SMT type': 0,
    'unknown SMT term': 0,
    'error parsing SMT-LIB': 0,
    'error parsing outer SMT-LIB': 0,
    'Failure to replay': 0,
    'not solved' : 0,
    'timeout' : 0,
    'could not be elaborated' : 0
}


# Colors 
colors = {
    'success': "#87bc45",
    'unknown error': "#f46a9b",
    'unknown SMT type': "#ea5545",
    'unknown SMT term': "#ef9b20",
    'error parsing SMT-LIB': "#edbf33",
    'error parsing outer SMT-LIB': "#ede15b",
    'Failure to replay': "#bdcf32",
    'not solved' : "#27aeef",
    'timeout' : "#b33dc6",
    'could not be elaborated' : "#b23346"
}    
        


def count_occurences(checking_entry,collect_res,collect_timeout_reason,collect_rec_error_reason):
  solver_config = checking_entry.get('solver_config', None)
  checking_time = checking_entry.get('checking_time', None)
  if solver_config == 'carcara':
    if checking_time is not None:
      if checking_time >= 0:
        collect_res['success'] += 1
      elif checking_time == -1:
        collect_res['unknown error'] += 1
      elif checking_time == -2:
        collect_res['unknown SMT type'] += 1
      elif checking_time == -3:
        collect_res['unknown SMT term'] += 1
      elif checking_time == -4:
        collect_res['error parsing SMT-LIB'] += 1
      elif checking_time == -5:
        collect_res['error parsing outer SMT-LIB'] += 1
      elif checking_time == -6:
        collect_res['Failure to replay'] += 1
        failed_rule = checking_entry.get('failed_rule', None)


        if failed_rule:
            if failed_rule in collect_rec_error_reason:
                collect_rec_error_reason[failed_rule] += 1
            else:
                collect_rec_error_reason[failed_rule] = 1
      elif checking_time == -7:
        collect_res['timeout'] += 1
        failed_rule = checking_entry.get('failed_rule', None)
        print(failed_rule)
        if failed_rule:
            if failed_rule in collect_timeout_reason:
                collect_timeout_reason[failed_rule] += 1
            else:
                collect_timeout_reason[failed_rule] = 1
  return [collect_res,collect_timeout_reason,collect_rec_error_reason]


# Initialize a counter for different failed rules
verit_benchs=[]
verit_elab_benchs=[]
failed_rules_verit = {}
rec_timeout_rules_verit = {}
failed_rules_elab_verit = {}
rec_timeout_rules_elab_verit = {}

# Count the entries in each category
for entry in data:
  print(entry['benchmark_name'])
  if entry['benchmark_name'].endswith("_elaborated.smt2"):
    for checking_entry in entry['checking']:
      verit_elab_benchs.append(entry['benchmark_name'].removesuffix("_elaborated.smt2"))
      res=count_occurences(checking_entry,verit_elab_res,rec_timeout_rules_elab_verit,failed_rules_elab_verit)
      verit_elab_res=res[0]
      rec_timeout_rules_elab_verit=res[1]
      failed_rules_elab_verit=res[2]
  else:
    for checking_entry in entry['checking']:
      verit_benchs.append(entry['benchmark_name'].removesuffix(".smt2"))
      res=count_occurences(checking_entry,verit_res,rec_timeout_rules_verit,failed_rules_verit)
      verit_res=res[0]
      rec_timeout_rules_verit=res[1]
      failed_rules_verit=res[2]
                
for vb in verit_benchs:
 if not vb in verit_elab_benchs:
  verit_elab_res['could not be elaborated'] += 1

for vb in verit_elab_benchs:
 if not vb in verit_benchs:
  print("Should not happen")
  print(vb)

print("-------------------------------------")                              
print("For non-elaborated benchmarks:")             
print("Failure distribution: ") 
print(verit_res)
print("Reasons for replay error:")              
print(failed_rules_verit)   
print("Reasons for timeout error:")              
print(rec_timeout_rules_verit)  
print("-------------------------------------")                              
print("For elaborated benchmarks:")             
print("Failure distribution: ") 
print(verit_elab_res)
print("Reasons for replay error:")              
print(failed_rules_elab_verit)   
print("Reasons for timeout error:")              
print(rec_timeout_rules_elab_verit)  
print("-------------------------------------")                              


    
    
# Filter out values with 0%
colors_verit = []
verit_res2 = {}
for category, value in verit_res.items():
    if value != 0:# and category != "timeout":
        colors_verit.append(colors[category])
        verit_res2[category] = value
    # Filter out verit_res that timed out

print(verit_res2)   
total_verit_res = sum(verit_res2.values())
verit_res2 = {key: (value / total_verit_res * 100) for key, value in verit_res2.items()}

# Filter out verit_elab_res with 0%
colors_verit_elab = []
verit_elab_res2 = {}
for category, value in verit_elab_res.items():
    if value != 0:# and category != "timeout":
        colors_verit_elab.append(colors[category])
        verit_elab_res2[category] = value
    # Filter out verit_elab_res that timed out

print(verit_elab_res2)   
total_verit_elab_res = sum(verit_elab_res2.values())
verit_elab_res2 = {key: (value / total_verit_elab_res * 100) for key, value in verit_elab_res2.items()}

 

# Create a pie chart
labels_verit = verit_res2.keys()
sizes_verit = verit_res2.values()
labels_elab_verit = verit_elab_res2.keys()
sizes_elab_verit = verit_elab_res2.values()



fig = plt.figure(figsize=(23,10),dpi=144)
fig.tight_layout(pad=15)
plt.subplots_adjust(wspace=0.5)
plt.subplots_adjust(left=-0.005)

ax1 = fig.add_subplot(121)
ax1.pie(sizes_verit, labels=labels_verit, colors=colors_verit, autopct='%1.1f%%', startangle=20, textprops={'fontsize': 25})
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
ax1.set_title('verit', size=25, y=1.1,loc='center')

ax2 = fig.add_subplot(122)
ax2.pie(sizes_elab_verit, labels=labels_elab_verit, colors=colors_verit_elab, autopct='%1.1f%%', startangle=20, textprops={'fontsize': 25})
ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
ax2.set_title('verit elaborated', size=25, y=1.1,loc='center')


plt.show()




# Count the failed rules for entries with checking_time equal to -6
for entry in data:
 if entry['benchmark_name'].endswith("_elaborated.smt2"):
  for checking_entry in entry['checking']:
    solver_config = checking_entry.get('solver_config', None)
    checking_time = checking_entry.get('checking_time', None)
    if solver_config == 'carcara':
      if checking_time == -6:
        failed_rule = checking_entry.get('failed_rule', None)
        if failed_rule:
            if failed_rule in failed_rules_elab_verit:
                failed_rules_elab_verit[failed_rule] += 1
            else:
                failed_rules_elab_verit[failed_rule] = 1
      if checking_time == -7:
        failed_rule = checking_entry.get('failed_rule', None)
        if failed_rule:
            if failed_rule in rec_timeout_rules_elab_verit:
                rec_timeout_rules_elab_verit[failed_rule] += 1
            else:
                rec_timeout_rules_elab_verit[failed_rule] = 1   
 else:          
    solver_config = checking_entry.get('solver_config', None)
    checking_time = checking_entry.get('checking_time', None)
    if solver_config == 'carcara':
      if checking_time == -6:
        failed_rule = checking_entry.get('failed_rule', None)
        if failed_rule:
            if failed_rule in failed_rules_verit:
                failed_rules_verit[failed_rule] += 1
            else:
                failed_rules_verit[failed_rule] = 1
      if checking_time == -7:
        failed_rule = checking_entry.get('failed_rule', None)
        if failed_rule:
            if failed_rule in rec_timeout_rules_verit:
                rec_timeout_rules_verit[failed_rule] += 1
            else:
                rec_timeout_rules_verit[failed_rule] = 1 

print("Timeout reasons verit proofs")                
print(rec_timeout_rules_verit)

print("Timeout reasons elaborated verit proofs")                
print(rec_timeout_rules_elab_verit)

# Create a pie chart for failed rules
labels_verit = failed_rules_verit.keys()
sizes_verit = failed_rules_verit.values()
labels_elab_verit = failed_rules_elab_verit.keys()
sizes_elab_verit = failed_rules_elab_verit.values()
print(labels_verit)

fig = plt.figure(figsize=(23,10),dpi=144)
fig.tight_layout(pad=15)
plt.suptitle('Distribution of Replay errors', fontsize=16)
plt.subplots_adjust(wspace=0.5)
plt.subplots_adjust(left=-0.005)

ax1 = fig.add_subplot(121)
ax1.pie(sizes_verit, labels=labels_verit, colors=["#2ca02c","#d62728","#ff7f0e", "#1f77b4"], autopct='%1.1f%%', startangle=140, textprops={'fontsize': 25})
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
ax1.set_title('verit reconstruction failure', size=25, y=1.1,loc='center')

ax2 = fig.add_subplot(122)
ax2.pie(sizes_elab_verit, labels=labels_elab_verit, colors=["#2ca02c","#d62728","#ff7f0e", "#1f77b4"], autopct='%1.1f%%', startangle=140, textprops={'fontsize': 25})
ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
ax2.set_title('verit elab reconstruction failure', size=25, y=1.1,loc='center')

plt.show()                


# Create a pie chart for failed rules
labels_verit = rec_timeout_rules_verit.keys()
sizes_verit = rec_timeout_rules_verit.values()
labels_elab_verit = rec_timeout_rules_elab_verit.keys()
sizes_elab_verit = rec_timeout_rules_elab_verit.values()


fig = plt.figure(figsize=(23,10),dpi=144)
fig.tight_layout(pad=15)
plt.suptitle('Distribution of Replay errors', fontsize=16)
plt.subplots_adjust(wspace=0.5)
plt.subplots_adjust(left=-0.005)

ax1 = fig.add_subplot(121)
ax1.pie(sizes_verit, labels=labels_verit, colors=["#2ca02c","#d62728","#ff7f0e", "#1f77b4"], autopct='%1.1f%%', startangle=140, textprops={'fontsize': 25})
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
ax1.set_title('verit reconstruction timeouts', size=25, y=1.1,loc='center')

ax2 = fig.add_subplot(122)
ax2.pie(sizes_elab_verit, labels=labels_elab_verit, colors=["#2ca02c","#d62728","#ff7f0e", "#1f77b4"], autopct='%1.1f%%', startangle=140, textprops={'fontsize': 25})
ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
ax2.set_title('verit elaborated reconstruction timeouts', size=25, y=1.1,loc='center')

plt.show() 
