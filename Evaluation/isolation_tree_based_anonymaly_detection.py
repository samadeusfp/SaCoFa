from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import get_log_representation
import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np
import pickle as pickle


def find_anonmalies_with_isolation_forest(log, original_features, original_log_df,result_path):
    log_features, feature_names_log = get_log_representation.get_representation(log,str_ev_attr=["concept:name"],str_tr_attr=[],num_ev_attr=[],num_tr_attr=[],str_evsucc_attr=["concept:name"])
    log_df = pd.DataFrame(log_features, columns=feature_names_log)

    features = np.union1d(original_features, feature_names_log)

    new_features_train = np.setxor1d(original_features,features)
    new_features_df = pd.DataFrame(columns=new_features_train)
    train_df = original_log_df.append(new_features_df)
    train_df = train_df.fillna(0)

    model = IsolationForest()
    model.fit(train_df)

    new_features_test = np.setxor1d(feature_names_log,features)
    new_features_df = pd.DataFrame(columns=new_features_test)
    test_df = log_df.append(new_features_df)
    test_df = test_df.fillna(0)

    log_df["scores"] = model.decision_function(test_df)
    results = dict()
    results["avg"] = log_df["scores"].mean()
    count_traces = log_df["scores"].count() + 1
    anonmalies = log_df[log_df.scores <= 0].shape[0]
    results["anonmaly_relative_frequency"] = anonmalies/count_traces
    print(results)

    with open(result_path,'wb') as file:
        pickle.dump(results,file)