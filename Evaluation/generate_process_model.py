from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
import sys
from pm4py.algo.discovery.inductive.parameters import Parameters
from pm4py.visualization.petrinet import visualizer as pn_visualizer


log_path = sys.argv[1]
out_path = sys.argv[2]

log = xes_importer.apply(log_path)
parameters = {Parameters.NOISE_THRESHOLD: 0.20}
model, initial_marking, final_marking = inductive_miner.apply(log,parameters,variant=inductive_miner.Variants.IMf)

parameters = {pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "png"}
gviz = pn_visualizer.apply(model, initial_marking, final_marking,parameters)
pn_visualizer.save(gviz,out_path)