import sys
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.evaluation.replay_fitness import evaluator as replay_fitness_evaluator
from pm4py.evaluation.precision import evaluator as precision_evaluator
from pm4py.evaluation.generalization import evaluator  as generalization_evaluator
from pm4py.evaluation.simplicity import evaluator as simplicity_evaluator
import pickle



def check_model_quality(original_log, anonymized_log,result_path):
    anonymized_model, anonymized_initial_marking, anonymized_final_marking = inductive_miner.apply(anonymized_log)
    results = dict()
    fitness = replay_fitness_evaluator.apply(original_log, anonymized_model, anonymized_initial_marking, anonymized_final_marking, variant=replay_fitness_evaluator.Variants.TOKEN_BASED)
    print("Fitness: " + str(fitness))
    results["fitness"] = fitness

    precision = precision_evaluator.apply(original_log, anonymized_model, anonymized_initial_marking, anonymized_final_marking, variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN)
    print("Precision: " + str(precision))
    results["precision"] = precision

    gen = generalization_evaluator.apply(original_log, anonymized_model, anonymized_initial_marking, anonymized_final_marking)
    print("Generalization: " + str(gen))
    results["generalization"] = gen

    simp = simplicity_evaluator.apply(anonymized_model)
    print("Simplicity: " + str(simp))
    results["simplicity"] = simp
    with open(result_path,'wb') as file:
        pickle.dump(results,file)

