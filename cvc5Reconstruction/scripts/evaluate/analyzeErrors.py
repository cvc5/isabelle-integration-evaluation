import json
import matplotlib.pyplot as plt
import sys

directory = '/home/lachnitt/Sources/isabelle-integration-evaluation/cvc5Reconstruction/result/'
input_file = directory + sys.argv[1] + '/all_checking.json'


# Read the JSON file
with open(input_file, 'r') as file:
    data = json.load(file)

# Initialize counters for different categories_without_rewrite
categories_without_rewrite = {
    'success': 0,
    'unknown error': 0,
    'unknown SMT type': 0,
    'unknown SMT term': 0,
    'error parsing SMT-LIB': 0,
    'error parsing outer SMT-LIB': 0,
    'Failure to replay': 0,
    'not solved' : 0,
    'Timeout' : 0
}

categories_with_rewrite = {
    'success': 0,
    'unknown error': 0,
    'unknown SMT type': 0,
    'unknown SMT term': 0,
    'error parsing SMT-LIB': 0,
    'error parsing outer SMT-LIB': 0,
    'Failure to replay': 0,
    'not solved' : 0,
    'Timeout' : 0
}

categories_verit = {
    'success': 0,
    'unknown error': 0,
    'unknown SMT type': 0,
    'unknown SMT term': 0,
    'error parsing SMT-LIB': 0,
    'error parsing outer SMT-LIB': 0,
    'Failure to replay': 0,
    'not solved' : 0,
    'Timeout' : 0
}


cvc5_with_rewrite=False
cvc5_without_rewrite=False
verit=False

# Count the entries in each category
for entry in data:
    with_rewrite=False
    without_rewrite=False 
    for checking_entry in entry['checking']:
      solver_config = checking_entry.get('solver_config', None)
      checking_time = checking_entry.get('checking_time', None)
      if solver_config == 'cvc5_without_rewrite':
        cvc5_without_rewrite=True;
        without_rewrite=True;
        if checking_time is not None:
          if checking_time >= 0:
              categories_without_rewrite['success'] += 1
          elif checking_time == -1:
              categories_without_rewrite['unknown error'] += 1
          elif checking_time == -2:
              categories_without_rewrite['unknown SMT type'] += 1
          elif checking_time == -3:
              categories_without_rewrite['unknown SMT term'] += 1
          elif checking_time == -4:
              categories_without_rewrite['error parsing SMT-LIB'] += 1
          elif checking_time == -5:
              categories_without_rewrite['error parsing outer SMT-LIB'] += 1
          elif checking_time == -6:
              categories_without_rewrite['Failure to replay'] += 1
          elif checking_time == -7:
              categories_without_rewrite['Timeout'] += 1
          else:
           print(checking_time)
      if solver_config == 'cvc5_with_rewrite':
        with_rewrite=True;
        cvc5_with_rewrite=True;
        if checking_time is not None:
          if checking_time >= 0:
              categories_with_rewrite['success'] += 1
          elif checking_time == -1:
              categories_with_rewrite['unknown error'] += 1
          elif checking_time == -2:
              categories_with_rewrite['unknown SMT type'] += 1
          elif checking_time == -3:
              categories_with_rewrite['unknown SMT term'] += 1
          elif checking_time == -4:
              categories_with_rewrite['error parsing SMT-LIB'] += 1
          elif checking_time == -5:
              categories_with_rewrite['error parsing outer SMT-LIB'] += 1
          elif checking_time == -6:
              categories_with_rewrite['Failure to replay'] += 1
          elif checking_time == -7:
              categories_with_rewrite['Timeout'] += 1
    if with_rewrite==False:
      categories_with_rewrite['not solved'] += 1
    if without_rewrite==False:
      categories_without_rewrite['not solved'] += 1      
      
      
      
# Colors 
colors = ["#87bc45", "#f46a9b","#ea5545", "#ef9b20", "#edbf33", "#ede15b", "#bdcf32",  "#27aeef", "#b33dc6"]  


# Filter out categories_without_rewrite with 0%
colors_without_rewrite = []
categories_without_rewrite2 = {}
for category, value in categories_without_rewrite.items():
    print(category)
    print(value)
    print("")
    if value != 0:
        colors_without_rewrite.append(colors.pop(0))
        categories_without_rewrite2[category] = value
        
total_categories_without_rewrite = sum(categories_without_rewrite2.values())
categories_without_rewrite2 = {key: (value / total_categories_without_rewrite * 100) for key, value in categories_without_rewrite2.items()}
      
# Filter out categories_with_rewrite with 0%
colors_with_rewrite = []
categories_with_rewrite2 = {}
for category, value in categories_with_rewrite.items():
    print(category)
    print(value)
    print("")
    if value != 0:
        colors_with_rewrite.append(colors.pop(0))
        categories_with_rewrite2[category] = value
        
total_categories_with_rewrite = sum(categories_with_rewrite2.values())
categories_with_rewrite2 = {key: (value / total_categories_with_rewrite * 100) for key, value in categories_with_rewrite2.items()}
     
if total_categories_without_rewrite != total_categories_with_rewrite:
  print("TOTALS ARE DIFFERENT!");
  print("with_rewrites",total_categories_with_rewrite)
  print("without_rewrites",total_categories_without_rewrite)
  
#categories_with_rewrite = {k: v for k, v in categories_with_rewrite.items() if v != 0}

# Create a pie chart
labels_without_rewrite = categories_without_rewrite2.keys()
sizes_without_rewrite = categories_without_rewrite2.values()
labels_with_rewrite = categories_with_rewrite2.keys()
sizes_with_rewrite = categories_with_rewrite2.values()

fig = plt.figure(figsize=(23,10),dpi=144)
fig.tight_layout(pad=15)
plt.subplots_adjust(wspace=0.5)
plt.subplots_adjust(left=-0.005)

if cvc5_without_rewrite == 1 :
  ax1 = fig.add_subplot(121)
  ax1.pie(sizes_without_rewrite, labels=labels_without_rewrite, colors=colors_without_rewrite, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 25})
  ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
  ax1.set_title('cvc5 without rewrites', size=25, y=1.1,loc='center')

if cvc5_with_rewrite == 1 :
 ax2 = fig.add_subplot(122)
 ax2.pie(sizes_with_rewrite, labels=labels_with_rewrite, colors=["#2ca02c","#d62728","#ff7f0e", "#1f77b4"], autopct='%1.1f%%', startangle=160, textprops={'fontsize': 25})
 ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
 ax2.set_title('cvc5 with rewrites', size=25, y=1.1,loc='center')


plt.show()


# Initialize a counter for different failed rules
failed_rules_without_rewrite = {}
rec_timeout_without_rewrite = {}
failed_rules_with_rewrite = {}
rec_timeout_with_rewrite = {}

# Count the failed rules for entries with checking_time equal to -6
for entry in data:
  for checking_entry in entry['checking']:
    solver_config = checking_entry.get('solver_config', None)
    checking_time = checking_entry.get('checking_time', None)
    if solver_config == 'cvc5_without_rewrite':
      if checking_time == -6:
        failed_rule = checking_entry.get('failed_rule', None)
        if failed_rule:
            if failed_rule in failed_rules_without_rewrite:
                failed_rules_without_rewrite[failed_rule] += 1
            else:
                failed_rules_without_rewrite[failed_rule] = 1
      if checking_time == -7:
        failed_rule = checking_entry.get('failed_rule', None)
        if failed_rule:
            if failed_rule in rec_timeout_without_rewrite:
                rec_timeout_without_rewrite[failed_rule] += 1
            else:
                rec_timeout_without_rewrite[failed_rule] = 1 
    if solver_config == 'cvc5_with_rewrite':
      if checking_time == -6:
        failed_rule = checking_entry.get('failed_rule', None)
        if failed_rule:
            if failed_rule in failed_rules_with_rewrite:
                failed_rules_with_rewrite[failed_rule] += 1
            else:
                failed_rules_with_rewrite[failed_rule] = 1             
      if checking_time == -7:
        failed_rule = checking_entry.get('failed_rule', None)
        if failed_rule:
            if failed_rule in rec_timeout_with_rewrite:
                rec_timeout_with_rewrite[failed_rule] += 1
            else:
                rec_timeout_with_rewrite[failed_rule] = 1             
# Create a pie chart for failed rules
labels_without_rewrite = failed_rules_without_rewrite.keys()
sizes_without_rewrite = failed_rules_without_rewrite.values()
labels_with_rewrite = failed_rules_without_rewrite.keys()
sizes_with_rewrite = failed_rules_without_rewrite.values()


fig = plt.figure(figsize=(23,10),dpi=144)
fig.tight_layout(pad=15)
plt.suptitle('Distribution of Replay errors', fontsize=16)
plt.subplots_adjust(wspace=0.5)
plt.subplots_adjust(left=-0.005)

if cvc5_without_rewrite == 1 :
  ax1 = fig.add_subplot(121)
  ax1.pie(sizes_without_rewrite, labels=labels_without_rewrite, colors=["#2ca02c","#d62728","#ff7f0e", "#1f77b4"], autopct='%1.1f%%', startangle=140, textprops={'fontsize': 25})
  ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
  ax1.set_title('cvc5 without rewrites', size=25, y=1.1,loc='center')

if cvc5_with_rewrite == 1 :
 ax2 = fig.add_subplot(122)
 ax2.pie(sizes_with_rewrite, labels=labels_with_rewrite, colors=["#2ca02c","#d62728","#ff7f0e", "#1f77b4"], autopct='%1.1f%%', startangle=160, textprops={'fontsize': 25})
 ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
 ax2.set_title('cvc5 with rewrites', size=25, y=1.1,loc='center')

plt.show()  




# Create a pie chart for failed rules
labels_verit = rec_timeout_without_rewrite.keys()
sizes_verit = rec_timeout_without_rewrite.values()

fig = plt.figure(figsize=(23,10),dpi=144)
fig.tight_layout(pad=15)
plt.suptitle('Distribution of Replay errors', fontsize=16)
plt.subplots_adjust(wspace=0.5)
plt.subplots_adjust(left=-0.005)

ax1 = fig.add_subplot(121)
ax1.pie(sizes_verit, labels=labels_verit, colors=["#2ca02c","#d62728","#ff7f0e", "#1f77b4"], autopct='%1.1f%%', startangle=140, textprops={'fontsize': 25})
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
ax1.set_title('without reconstruction timeouts', size=25, y=1.1,loc='center')

plt.show() 

              

