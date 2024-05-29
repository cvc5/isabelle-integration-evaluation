import json
import matplotlib.pyplot as plt
import sys

directory = '/home/lachnitt/Sources/isabelle-integration-evaluation/cvc5Reconstruction/result/'
input_file = directory + sys.argv[1] + '/all_checking.json'

# Read the JSON file
with open(input_file, 'r') as file:
    data = json.load(file)


# Initialize sums and counts for each solver configuration and rare_rewrite
labels = ["total checking time with rewrites", "total amount with rewrites", "total checking time without rewrites", "total amount without rewrites" "sum_rare_rewrite_with_rewrite", "count_rare_rewrite_with_rewrite"]
with_rewrite = [0, 0, 0, 0, 0, 0, 0, 0]  
without_rewrite = [0, 0, 0, 0]  
reconstructed_with_rewrite=0
reconstructed_without_rewrite=0
total = len(data)

#TODO: Include parsing?
# Iterate over the data
for entry in data:
    has_with_rewrite = False
    has_without_rewrite = False
    for checking_entry in entry["checking"]:
        if checking_entry["solver_config"] == "cvc5_with_rewrite":
            has_with_rewrite = True
        elif checking_entry["solver_config"] == "cvc5_without_rewrite":
            has_without_rewrite = True
            
    if has_with_rewrite :
      reconstructed_with_rewrite += 1

    if has_without_rewrite :
      reconstructed_without_rewrite += 1
           
    # Only count if both solver configurations are present
    if has_with_rewrite and has_without_rewrite:
        for idx, checking_entry in enumerate(entry["checking"]):
            if checking_entry["solver_config"] == "cvc5_with_rewrite":
                with_rewrite[0] += checking_entry["checking_time"]
                with_rewrite[1] += 1
                if "detail" in checking_entry:
                 if "all_simplify" in checking_entry["detail"]:
                    with_rewrite[2] += sum(checking_entry["detail"]["all_simplify"])
                    with_rewrite[3] += len(checking_entry["detail"]["all_simplify"])
                 if "rare_rewrite" in checking_entry["detail"]:
                    with_rewrite[4] += sum(checking_entry["detail"]["rare_rewrite"])
                    with_rewrite[5] += len(checking_entry["detail"]["rare_rewrite"])
                 if "hole" in checking_entry["detail"]:
                    with_rewrite[6] += sum(checking_entry["detail"]["hole"])
                    with_rewrite[7] += len(checking_entry["detail"]["hole"])
                
            elif checking_entry["solver_config"] == "cvc5_without_rewrite":
                without_rewrite[0] += checking_entry["checking_time"]
                without_rewrite[1] += 1
                if "detail" in checking_entry:
                 if "all_simplify" in checking_entry["detail"]:
                    without_rewrite[2] += sum(checking_entry["detail"]["all_simplify"])
                    without_rewrite[3] += len(checking_entry["detail"]["all_simplify"])

# Calculate the averages
averages_with_rewrite = [with_rewrite[0] / with_rewrite[1],(with_rewrite[2] + with_rewrite[4] + with_rewrite[6])/(without_rewrite[3])]
averages_without_rewrite = [without_rewrite[i] / without_rewrite[i + 1] if without_rewrite[i + 1] > 0 else 0 for i in range(0, 4, 2)]

print('Total nr of benchmarks', total)
print('Total nr reconstructed with rewrites',reconstructed_with_rewrite)
print('Total nr reconstructed without rewrites',reconstructed_without_rewrite)
print('\n')

print('In the benchmarks with rewrites')
print('Nr of rare rewrites',(with_rewrite[5]))
print('Nr of holes',(with_rewrite[7]))
print('\n')

print('In the benchmarks without rewrites')
print('Nr of all_simplifies',(without_rewrite[3]))
print('\n')


print('For all benchmarks where cvc5_with_rewrite and cvc5_without_rewrite succeed:')
print('Average checking time for cvc5_with_rewrite: {0:.2f} s'.format(averages_with_rewrite[0]))
print('Average checking time for cvc5_without_rewrite: {0:.2f} s'.format(averages_without_rewrite[0]))

print('Average checking time for rewrite steps with cvc5_with_rewrite: {0:.2f} ms'.format(averages_with_rewrite[1]/1000))
print('Average checking time for rewrite steps with cvc5_without_rewrite: {0:.2f} ms'.format(averages_without_rewrite[1]/1000))



