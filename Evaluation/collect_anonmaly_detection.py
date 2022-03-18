import sys
import pandas as pd
import pickle
import os

log_name = sys.argv[1]
base_path = sys.argv[2]
result_dir_path = sys.argv[3]

epsRange = [1.0,0.1,0.01]
tries = 10                                                          # how many tries per epsilon
modeRange = ['laplace','ba_prune','ba','df_laplace','df_exp1','df_exp2','df_exp3','df_exp4','df_exp5']
max_k_list = [1,2,3,4,5]
df = pd.DataFrame()
result_file_path = os.path.join(result_dir_path, log_name + "_anomaly_detection_results.csv")

for mode in modeRange:
    for eps in epsRange:
        for i in range(tries):
            file_path = os.path.join(base_path, log_name + '_' + str(eps) + '_' + mode + '_' + str(i) + "_anomaly_detection.pickle")
            if os.path.exists(file_path):
                data = dict()
                file = open(file_path, 'rb')
                data_results = pickle.load(file)
                data["log_name"] = log_name
                data["run"] = i + 1
                data["algorithm"] = mode
                data["epsilon"] = eps
                data["avg"] = data_results["avg"]
                data["anonmaly_relative_frequency"] = data_results["anonmaly_relative_frequency"]
                df = df.append(data,ignore_index=True)
df.to_csv(result_file_path,index=False,sep=';')