from isolation_tree_based_anonymaly_detection import find_anonmalies_with_isolation_forest as find_anonmalies
from pm4py.objects.log.util import get_log_representation
import pandas as pd
import sys
from pm4py.objects.log.importer.xes import importer as xes_importer

log_name = sys.argv[1]
base_path = sys.argv[2]
original_log_path = sys.argv[3]
epsRange = [0.1,0.01,1.0]
#modeRange = ['occured','ba_prune']
#modeRange = ['laplace','ba','ba_prune']
modeRange = ['df_exp','df_laplace']
max_k_list = [1,2,3,4,5]

tries = 10


original_log = xes_importer.apply(original_log_path)
original_log_features, feature_names_original_log = get_log_representation.get_representation(original_log,
                                                                                              str_ev_attr=[ "concept:name"],
                                                                                              str_tr_attr=[],
                                                                                              num_ev_attr=[],
                                                                                              num_tr_attr=[],
                                                                                              str_evsucc_attr=["concept:name"])
original_log_df = pd.DataFrame(original_log_features, columns=feature_names_original_log)

for mode in modeRange:
    for eps in epsRange:
        for i in range(tries):
            if not mode == 'df_exp':
                anonymized_log_path = base_path + log_name + '_' + str(eps) + '_' + mode + '_' + str(i) + ".xes"
                anonymized_log = xes_importer.apply(anonymized_log_path)
                result_path = base_path + log_name + '_' + str(eps) + '_' + mode + '_' + str(
                    i) + "_anomaly_detection.pickle"
                find_anonmalies(log=anonymized_log, original_features=feature_names_original_log,
                                original_log_df=original_log_df, result_path=result_path)
            else:
                for max_k in max_k_list:
                    anonymized_log_path = base_path  + log_name + '_' + str(eps) + '_max_k' + str(
                                max_k) + '_' + mode + '_' + str(i) + ".xes"
                    anonymized_log = xes_importer.apply(anonymized_log_path)
                    result_path = base_path + log_name + '_' + str(eps) + '_' + mode + str(max_k) + '_' + str(i) + "_anomaly_detection.pickle"
                    find_anonmalies(log=anonymized_log,original_features=feature_names_original_log,original_log_df=original_log_df,result_path=result_path)


