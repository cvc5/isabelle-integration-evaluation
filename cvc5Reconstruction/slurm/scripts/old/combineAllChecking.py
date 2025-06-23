import json
import pandas as pd
import sys
import os
from pathlib import Path
pd.set_option('display.max_rows', 10)
pd.set_option('display.max_colwidth', None)

def merge_lists(list1, list2):
    if pd.isna(list1) and pd.isna(list2):
        return np.nan
    if pd.isna(list1):
        return list2
    if pd.isna(list2):
        return list1
    else:
        return list1 + list2

def combine(checking1,checking2,checking3,out_file):
    merged=pd.DataFrame()
    error=pd.DataFrame()
    checking_data1 = pd.read_json(Path(checking1))
    checking_data2 = pd.read_json(Path(checking2))
    checking_data3 = pd.read_json(Path(checking3))
    #print(checking_data2[['benchmark_name','benchmark_path']])
    if checking_data1.empty and checking_data2.empty and checking_data3.empty:
        print("all files empty")
        exit()
    elif checking_data1.empty and checking_data2.empty:
      merged2 = checking_data3
    elif checking_data2.empty and checking_data3.empty:
      merged2 = checking_data1
    elif checking_data2.empty and checking_data3.empty:
      merged2 = checking_data1
    else:
      if checking_data1.empty:
          merged1=checking_data2
      elif checking_data2.empty:
          merged1=checking_data1
      else:
        merged1= checking_data1.merge(checking_data2,how='outer',on=['benchmark_path'],suffixes=('_x','_y'))
        merged1['checking'] = merged1.apply(lambda row: merge_lists(row['checking_x'], row['checking_y']), axis=1)
        merged1 = merged1.drop(columns=['checking_x','checking_y'])
        merged1 = merged1.drop(columns=[col for col in ['benchmark_name_x','benchmark_name_checking_y'] in merged1.columns])

      #merged1.to_json(Path(out_file+"_test_merged1"), indent=1, orient = 'records', compression = 'infer', index = 'false')    
      if checking_data3.empty:
          merged2=merged1
      else:
        merged2= merged1.merge(checking_data3, how='outer', on=['benchmark_path'],suffixes=('_z','_a'))
        merged2['checking'] = merged2.apply(lambda row: merge_lists(row['checking_z'], row['checking_a']), axis=1)
        merged2 = merged2.drop(columns=['checking_z','checking_a'])
        merged2 = merged2.drop(columns=[col for col in ['benchmark_name_a','benchmark_name_checking_z'] in merged2.columns])
        #merged2.to_json(Path(out_file+"_test"), indent=1, orient = 'records', compression = 'infer', index = 'false') 
    merged2.to_json(Path(out_file), indent=1, orient = 'records', compression = 'infer', index = 'false')    

if __name__ == "__main__":
    combine(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])

