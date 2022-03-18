from pm4py.objects.log.importer.xes import importer as xes_importer
import sys
import os
import pandas as pd

log_name = sys.argv[1]
base_path = sys.argv[2]
result_dir_path = sys.argv[3]
epsRange = [0.1,0.01,1.0]
modeRange = ['laplace','ba_prune','occured','ba','df_exp','df_laplace']
max_k_list = [1,2,3,4,5]


result_file_path = os.path.join(result_dir_path, log_name + "_log_count.csv")

tries = 10

def count_log_size(log_path):
    log = xes_importer.apply(log_path)
    return len(log)

df = pd.DataFrame()
data = dict()

for mode in modeRange:
    for eps in epsRange:
        for i in range(tries):
            if not mode == 'df_exp':
                anonymized_log_path = base_path + log_name + '_' + str(eps) + '_' + mode + '_' + str(i) + ".xes"
                count_log_size(anonymized_log_path)
                data["log_name"] = log_name
                data["run"] = i + 1
                data["algorithm"] = mode
                data["epsilon"] = eps
                data["count_traces"] = count_log_size(anonymized_log_path)
                df = df.append(data, ignore_index=True)
            else:
                for max_k in max_k_list:
                    anonymized_log_path = base_path + log_name + '_' + str(eps) + '_max_k' + str(
                        max_k) + '_' + mode + '_' + str(i) + ".xes"
                    data["log_name"] = log_name
                    data["run"] = i + 1
                    data["algorithm"] = mode + str(max_k)
                    data["epsilon"] = eps
                    count_log_size(anonymized_log_path)
                    df = df.append(data, ignore_index=True)
df.to_csv(result_file_path,index=False,sep=';')