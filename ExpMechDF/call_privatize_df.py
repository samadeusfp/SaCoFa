from opyenxes.data_in.XUniversalParser import XUniversalParser
from opyenxes.classification.XEventNameClassifier import XEventNameClassifier
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log import log as event_log
import datetime
from dateutil.tz import tzutc

from privatize_laplace import privatize_df_laplace
from privatize_df_occured import privatize_df_occured
from privatize_df_exp import privatize_df_exp

TRACE_START = "TRACE_START"
TRACE_END = "TRACE_END"
EVENT_DELIMETER = ">>>"

basePath = '/Users/stephan/SaCoFa_EventLogs'          # path to the folder containing all the event logs
logName = 'traffic_fines'
max_k_list = [1,2,3,4,5]

# the preferrable file structure is given in the README

inPath = basePath + '/Logs/' + logName + '.xes'
epsRange = [1.0,0.1,0.01]            # range of epsilon
tries = 10
modeRange = ['df_exp','df_laplace']


def main():
    log_x, log_pm4py = readLogFile(inPath)
    for mode in modeRange:
        for eps in epsRange:
            for i in range(tries):
                if mode == 'df_laplace':
                    out_path = basePath + '/Out/' + logName + '/' + logName + '_' + str(eps) + '_' + mode + '_' + str(i) + ".xes"
                    private_log = privatize_df_laplace.privatize_tracevariants(log_x, log_pm4py, eps)
                    xes_exporter.apply(private_log, out_path)
                elif mode == 'df_exp':
                    for max_k in max_k_list:
                        out_path = basePath + '/Out/' + logName + '/' + logName + '_' + str(eps) + '_max_k' + str(
                            max_k) + '_' + mode + '_' + str(i) + ".xes"
                        private_log = privatize_df_exp.privatize_tracevariants(log_x, log_pm4py, eps,max_k)
                        xes_exporter.apply(private_log,out_path)
    print("Done for all eps for all tries.")


def readLogFile(file):
    with open(file) as log_file:
        return XUniversalParser().parse(log_file), xes_importer.apply(file)

main()
