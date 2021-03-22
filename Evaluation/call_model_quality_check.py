from check_model_quality import check_model_quality as check_model_quality
import sys
from pm4py.objects.log.importer.xes import importer as xes_importer

log_name = sys.argv[1]
base_path = sys.argv[2]
original_log_path = sys.argv[3]
epsRange = [0.1,0.01,1.0]
#modeRange = ['occured','ba_prune']
modeRange = ['laplace','ba_prune','occured','ba']

tries = 10


original_log = xes_importer.apply(original_log_path)
for mode in modeRange:
    for eps in epsRange:
        for i in range(tries):
            anonymized_log_path = base_path + log_name + '_' + str(eps) + '_' + mode + '_' + str(i) + ".xes"
            anonymized_log = xes_importer.apply(anonymized_log_path)
            result_path = base_path + log_name + '_' + str(eps) + '_' + mode + '_' + str(i) + ".pickle"
            check_model_quality(original_log=original_log,anonymized_log=anonymized_log,result_path=result_path)

