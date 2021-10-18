from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.evaluation.replay_fitness import evaluator as replay_fitness_evaluator
from pm4py.evaluation.precision import evaluator as precision_evaluator
from pm4py.evaluation.generalization import evaluator  as generalization_evaluator
from pm4py.objects.log.util import get_log_representation
from sklearn.ensemble import IsolationForest


import pandas as pd
import sys

original_log_path = sys.argv[1]

original_log = xes_importer.apply(original_log_path)

model, initial_marking, final_marking = inductive_miner.apply(original_log)

fitness = replay_fitness_evaluator.apply(original_log, model, initial_marking,final_marking,variant=replay_fitness_evaluator.Variants.TOKEN_BASED)
print(fitness)
fitness = fitness["average_trace_fitness"]
precision = precision_evaluator.apply(original_log, model, initial_marking,final_marking,variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN)
print(str(precision))
fscore = 2 * precision * fitness / (precision + fitness)
print("Fscore of: " + str(fscore))

generalization = generalization_evaluator.apply(original_log, model, initial_marking,final_marking)
print("Generalization of: " + str(generalization))

log_features, feature_names_log = get_log_representation.get_representation(original_log, str_ev_attr=["concept:name"],
                                                                            str_tr_attr=[], num_ev_attr=[],
                                                                            num_tr_attr=[],
                                                                            str_evsucc_attr=["concept:name"])
log_df = pd.DataFrame(log_features, columns=feature_names_log)

model = IsolationForest()
model.fit(log_df)

log_df["scores"] = model.decision_function(log_df)
count_traces = log_df["scores"].count() + 1
anonmalies = log_df[log_df.scores <= 0].shape[0]
anonmaly_relative_frequency = anonmalies / count_traces
print("Relative frequency anonmalies: " + str(anonmaly_relative_frequency))