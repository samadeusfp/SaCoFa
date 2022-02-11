from check_model_quality import check_model_quality as check_model_quality
import sys
from pm4py.objects.log.importer.xes import importer as xes_importer

log_name = sys.argv[1]
base_path = sys.argv[2]
original_log_path = sys.argv[3]
epsRange = [0.1,0.01,1.0]
#modeRange = ['occured','ba_prune']
#modeRange = ['laplace','ba_prune','occured','ba']
modeRange =  ['df_exp','df_laplace']
max_k_list = [1,2,3,4,5]



tries = 10

def run_model_quality_check(anonymized_log_path,base_path,log_name,eps,mode,i,max_k=''):
    anonymized_log = xes_importer.apply(anonymized_log_path)
    result_path = base_path + log_name + '_' + str(eps) + '_' + mode + max_k + '_' + str(i) + ".pickle"
    check_model_quality(original_log=original_log, anonymized_log=anonymized_log, result_path=result_path)


original_log = xes_importer.apply(original_log_path)
for mode in modeRange:
    for eps in epsRange:
        for i in range(tries):
            if not mode == 'df_exp':
                anonymized_log_path = base_path + log_name + '_' + str(eps) + '_' + mode + '_' + str(i) + ".xes"
                run_model_quality_check(anonymized_log_path, base_path, log_name, eps, mode, i)
            else:
                for max_k in max_k_list:
                    anonymized_log_path = base_path  + log_name + '_' + str(eps) + '_max_k' + str(
                                max_k) + '_' + mode + '_' + str(i) + ".xes"
                    run_model_quality_check(anonymized_log_path, base_path, log_name, eps, mode, i,str(max_k))

