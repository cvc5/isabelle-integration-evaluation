import json
import matplotlib.pyplot as plt
import sys
import numpy as np

directory = '/home/lachnitt/Sources/isabelle-integration-evaluation/cvc5Reconstruction/result/'
input_file = directory + sys.argv[1] + '/all_checking.json'
mode="cvc5_without_rewrite"

def plot_times(input_data):
 
    fig = plt.figure(figsize =(10, 7))
    plt.boxplot(input_data.values(),labels=input_data.keys())
    plt.xlabel('Rule Name')
    plt.ylabel('Time to check')
    plt.title('Checking time per rule type')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def plot_entries(input_data):
    """
    Plots the number of entries per rule in the input data.

    Args:
    input_data (dict): Dictionary where keys are rule names and values are lists of times it took to check that rule.
    """
    # Extract the keys and the number of entries in each list
    fields = list(input_data.keys())
    entry_counts = [len(values) for values in input_data.values()]

    # Plotting the data
    plt.figure(figsize=(10, 6))
    plt.bar(fields, entry_counts, color='skyblue')
    plt.xlabel('Rule Name')
    plt.ylabel('Number of Occurrences')
    plt.title('Number of Occurrences per Rule')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Display the graph
    plt.show()

# Read the JSON file
with open(input_file, 'r') as file:
    data = json.load(file)

details_per_rule = {}

for entry in data:
  for checking_entry in entry["checking"]:
    if checking_entry["solver_config"] == mode:
      if "detail" in checking_entry:
        details = checking_entry['detail']
        for rule_times in details:
          if rule_times == "parsing":
            continue;
          if rule_times == "__normalized_input":
            continue;
          if rule_times == "__local_input":
            continue;
          elif rule_times in details_per_rule :
            details_per_rule[rule_times] += details[rule_times]
          else:
            details_per_rule[rule_times] = details[rule_times]


plot_entries(details_per_rule)
plot_times(details_per_rule)




