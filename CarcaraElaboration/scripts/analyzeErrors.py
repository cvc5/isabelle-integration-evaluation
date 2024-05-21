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

# Count the entries in each category
for entry in data:

    for checking_entry in entry['checking']:
      solver_config = checking_entry.get('solver_config', None)
      checking_time = checking_entry.get('checking_time', None)
      if solver_config == 'carcara':
        if checking_time is not None:
          if checking_time >= 0:
              verit_res['success'] += 1
          elif checking_time == -1:
              verit_res['unknown error'] += 1
          elif checking_time == -2:
              verit_res['unknown SMT type'] += 1
          elif checking_time == -3:
              verit_res['unknown SMT term'] += 1
          elif checking_time == -4:
              verit_res['error parsing SMT-LIB'] += 1
          elif checking_time == -5:
              verit_res['error parsing outer SMT-LIB'] += 1
          elif checking_time == -6:
              verit_res['Failure to replay'] += 1
          elif checking_time == -7:
              verit_res['timeout'] += 1

      
      
# Colors 
colors = ["#87bc45", "#f46a9b","#ea5545", "#ef9b20", "#edbf33", "#ede15b", "#bdcf32",  "#27aeef", "#b33dc6"]  

print(verit_res)
# Filter out verit_res with 0%
colors_verit = []
verit_res2 = {}
for category, value in verit_res.items():
    if value != 0:# and category != "timeout":
        colors_verit.append(colors.pop(0))
        verit_res2[category] = value
    # Filter out verit_res that timed out

print(verit_res2)   
total_verit_res = sum(verit_res2.values())
verit_res2 = {key: (value / total_verit_res * 100) for key, value in verit_res2.items()}
 

# Create a pie chart
labels_verit = verit_res2.keys()
sizes_verit = verit_res2.values()

fig = plt.figure(figsize=(23,10),dpi=144)
fig.tight_layout(pad=15)
plt.subplots_adjust(wspace=0.5)
plt.subplots_adjust(left=-0.005)

ax1 = fig.add_subplot(121)
ax1.pie(sizes_verit, labels=labels_verit, colors=colors_verit, autopct='%1.1f%%', startangle=20, textprops={'fontsize': 25})
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
ax1.set_title('verit', size=25, y=1.1,loc='center')

plt.show()


# Initialize a counter for different failed rules
failed_rules_verit = {}
rec_timeout_rules_verit = {}

# Count the failed rules for entries with checking_time equal to -6
for entry in data:
  for checking_entry in entry['checking']:
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
                
# Create a pie chart for failed rules
labels_verit = failed_rules_verit.keys()
sizes_verit = failed_rules_verit.values()


fig = plt.figure(figsize=(23,10),dpi=144)
fig.tight_layout(pad=15)
plt.suptitle('Distribution of Replay errors', fontsize=16)
plt.subplots_adjust(wspace=0.5)
plt.subplots_adjust(left=-0.005)

ax1 = fig.add_subplot(121)
ax1.pie(sizes_verit, labels=labels_verit, colors=["#2ca02c","#d62728","#ff7f0e", "#1f77b4"], autopct='%1.1f%%', startangle=140, textprops={'fontsize': 25})
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
ax1.set_title('verit reconstruction failure', size=25, y=1.1,loc='center')

plt.show()                


# Create a pie chart for failed rules
labels_verit = rec_timeout_rules_verit.keys()
sizes_verit = rec_timeout_rules_verit.values()

fig = plt.figure(figsize=(23,10),dpi=144)
fig.tight_layout(pad=15)
plt.suptitle('Distribution of Replay errors', fontsize=16)
plt.subplots_adjust(wspace=0.5)
plt.subplots_adjust(left=-0.005)

ax1 = fig.add_subplot(121)
ax1.pie(sizes_verit, labels=labels_verit, colors=["#2ca02c","#d62728","#ff7f0e", "#1f77b4"], autopct='%1.1f%%', startangle=140, textprops={'fontsize': 25})
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
ax1.set_title('verit reconstruction timeouts', size=25, y=1.1,loc='center')

plt.show() 
