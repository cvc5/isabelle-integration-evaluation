import json
import pandas as pd
import sys
import math


def combine(solving_input_file1,checking_input_file2,both_output_file):
    #pd.set_option('display.max_columns', 100)
    #pd.set_option('display.width', 1000)
    pd.options.display.width = 100
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('display.max_columns', None)
    pd.set_option("max_colwidth", None)
    solving_data1 = pd.read_json(solving_input_file1)
    solving_data2 = pd.read_json(checking_input_file2)
    print("solving file",solving_input_file1,len(solving_data1))
    print("checking file",checking_input_file2,len(solving_data2))

    solving_data1.benchmark_path=solving_data1.benchmark_path.astype(str)
    solving_data1.benchmark_path=solving_data1.benchmark_path.str.encode('utf-8')
    solving_data2.benchmark_path=solving_data2.benchmark_path.astype(str)
    solving_data2.benchmark_path=solving_data2.benchmark_path.str.encode('utf-8')
    #print(solving_data2.dtypes.to_dict())
    #print(solving_data1)

    #filter by libary
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
            merged = g1.merge(g2,how='outer',on=['library_name','benchmark_path'],suffixes=('_x','_y'))
            if 'benchmark_name_y' in merged.columns:
              merged.drop('benchmark_name_y', axis=1, inplace=True)
              merged.rename({'benchmark_name_x': 'benchmark_name'}, axis='columns',inplace=True)
            if 'set_name_y' in merged.columns:
              merged.drop('set_name_y', axis=1, inplace=True)
              merged.rename({'set_name_x': 'set_name'}, axis='columns',inplace=True)
            print(merged)
            #print("merged",merged)

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
    merged_df.to_json(both_output_file, orient = 'records', indent=1, compression = 'infer', index = 'false')    

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage <json1> <json2> <out_json>")
        sys.exit(0)
    combine(sys.argv[1], sys.argv[2], sys.argv[3])

