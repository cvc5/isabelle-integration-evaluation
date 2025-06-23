import json
import pandas as pd
import sys
import math
import numpy as np

def drop_if_nan(merged,v):

    v1 = v +'_x'
    v2 = v +'_y'
    merged[v] = np.where(
              merged[v1].notna(), merged[v1], 
              merged[v2]
            )
    merged=merged.drop(v1,axis=1)
    merged=merged.drop(v2,axis=1)



    return merged

def combine(solving_input_file1,solving_input_file2,solving_output_file):
    #pd.set_option('display.max_columns', 100)
    #pd.set_option('display.width', 1000)
    pd.options.display.width = 100
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('display.max_columns', None)
    pd.set_option("max_colwidth", None)
    solving_data1 = pd.read_json(solving_input_file1)
    solving_data2 = pd.read_json(solving_input_file2)
    print("first file",solving_input_file1,len(solving_data1))
    print("second file",solving_input_file2,len(solving_data2))

    solving_data1.benchmark_path=solving_data1.benchmark_path.astype(str)
    solving_data1.benchmark_path=solving_data1.benchmark_path.str.encode('utf-8')
    solving_data2.benchmark_path=solving_data2.benchmark_path.astype(str)
    solving_data2.benchmark_path=solving_data2.benchmark_path.str.encode('utf-8')
    #print(solving_data2.dtypes.to_dict())
    #print(solving_data1)
    grouped_dfs1 = [group for _, group in solving_data1.groupby('library_name')]
    grouped_dfs2 = [group for _, group in solving_data2.groupby('library_name')]
    merged_lib=[]
    for g1 in grouped_dfs1:
      l1=g1['library_name']
      if len(l1) > 1:
       found=False
       for g2 in grouped_dfs2:
          l2=g2['library_name']
          if len(l2) > 1 and (str(l1.iloc[0]) == str(l2.iloc[0])):
            found=True

            merged= solving_data1.merge(solving_data2,how='outer',on=['library_name','benchmark_path'],suffixes=('_x','_y'))
            merged=drop_if_nan(merged,'benchmark_name')
            merged=drop_if_nan(merged,'benchmark_steps')

            for index, bench in merged.iterrows():

              if ('checking_x' in bench.keys()) and (isinstance(bench['checking_x'], list)):
                if ('checking_y' in bench.keys()) and (isinstance(bench['checking_y'], list)):
                  #both are present
                  for checking_entry_x in bench['checking_x']:
                      for checking_entry_y in bench['checking_y']:
                        if checking_entry_y['solver_config'] == checking_entry_x['solver_config']:
                           checking_entry_x.update(checking_entry_y)
                           bench['checking_y'].remove(checking_entry_y)
                  for checking_entry_y in bench['checking_y']:
                    bench['checking_x'].append(checking_entry_y)
                #if solving_y is empty nothing happens
              else: #if solving_x is empty use solving_y
                bench['checking_x']=bench['checking_y']
              merged.iloc[index]=(bench)
            
            if 'checking_y' in merged.keys():
              merged=merged.drop('checking_y',axis=1)
            if 'checking_x' in merged.keys():
              merged = merged.rename({'checking_x': 'checking'}, axis='columns')
            merged_lib.append(merged)
      if not found :
        #print("did not found current library of g1 in g2",len(merged_lib))
        merged_lib.append(g1)
        #print("added g1",len(merged_lib))
    for g2 in grouped_dfs2:
      l2=g2['library_name']
      if len(l2) > 1:
       found=False
       for g1 in grouped_dfs1:
          l1=g1['library_name']
          if len(l1) > 1 and (str(l1.iloc[0]) == str(l2.iloc[0])):
            found=True
       if not found :
          #print("did not found current library of g2 in g1",len(merged_lib))
          merged_lib.append(g2)

    merged_df  = pd.DataFrame()
    merged_df = pd.concat(merged_lib,ignore_index=True)
    merged_df.to_json(solving_output_file, orient = 'records', indent=1, compression = 'infer', index = 'false')





if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage <json1> <json2> <out_json>")
        sys.exit(0)
    combine(sys.argv[1], sys.argv[2], sys.argv[3])

