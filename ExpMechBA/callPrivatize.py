from opyenxes.data_in.XUniversalParser import XUniversalParser
from opyenxes.classification.XEventNameClassifier import XEventNameClassifier
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log import log as event_log
import datetime
from dateutil.tz import tzutc

from privatize_occured import privatize_tv as privatize_bauer
from privatize_ba import privatize_ba
from privatize_laplace import privatize_laplace


TRACE_START = "TRACE_START"
TRACE_END = "TRACE_END"
EVENT_DELIMETER = ">>>"

P = 3
P_smart = 2
N = 10

basePath = '/Users/stephan/SaCoFa_EventLogs'          # path to the folder containing all the event logs
logName = 'CoSeLoG'                             # the preferrable file structure is given in the README

inPath = basePath + '/Logs/' + logName + '.xes'
epsRange = [1.0]            # range of epsilon
tries = 10
#modeRange = ['laplace','ba','ba_prune','ba']
modeRange = ['ba','laplace','occured','ba_prune']
#modeRange = ['occured','ba',','ba_prune','ba_prune_multi']


def main():
    log = readLogFile(inPath)
    counter = 1
    for mode in modeRange:
        for eps in epsRange:
            for i in range(tries):
                print("Run " +  str(counter))

                if mode == 'occured':
                    sanitized_frequencies = privatize_bauer.privatize_tracevariants(log=log, epsilon=eps, P=P, N=N)

                elif mode == 'ba':
                    sanitized_frequencies = privatize_ba.privatize_tracevariants(log=log, epsilon=eps, P=P, N=N)

                elif mode == 'ba_multi':
                    sanitized_frequencies = privatize_ba.privatize_tracevariants(log=log, epsilon=eps, P=P, N=N,sensitivity=3)

                elif mode == 'ba_prune':
                    sanitized_frequencies = privatize_ba.privatize_tracevariants(log=log, epsilon=eps, P=P, N=N,smart_pruning=True,P_smart=P_smart)

                elif mode == 'ba_prune_multi':
                    sanitized_frequencies = privatize_ba.privatize_tracevariants(log=log, epsilon=eps, P=P, N=N,smart_pruning=True,P_smart=P_smart,sensitivity=3)

                elif mode == 'laplace':
                    sanitized_frequencies = privatize_laplace.privatize_tracevariants(log=log, epsilon=eps, P=P, N=N)
                counter = counter +1
                print("Done: " + mode + " eps = " + str(eps) + ", try = " + str(i) + '\n')

                print("Writing to .csv...")
                outPath_csv = basePath + '/Out/' + logName  + '/' + logName + '_' + str(eps) + '_' + mode + '_' + str(i) + ".csv"
                write_to_csv(frequencies=sanitized_frequencies, path=outPath_csv)

                print("Writing to .xes...")
                outPath_xes = basePath + '/Out/' + logName + '/' + logName  +  '_' + str(eps) + '_' + mode + '_' + str(i) + ".xes"
                write_to_xes(frequencies=sanitized_frequencies, path=outPath_xes)

    print("Done for all eps for all tries.")


def readLogFile(file):
    with open(file) as log_file:
        return XUniversalParser().parse(log_file)


def generate_pm4py_log(trace_frequencies):
    log = event_log.EventLog()
    trace_count = 0
    for variant in trace_frequencies.items():
        frequency=variant[1]
        activities=variant[0].split(EVENT_DELIMETER)
        for i in range (0,frequency):
            trace = event_log.Trace()
            trace.attributes["concept:name"] = trace_count
            trace_count = trace_count + 1
            for activity in activities:
                if not TRACE_END in activity:
                    event = event_log.Event()
                    event["concept:name"] = str(activity)
                    event["time:timestamp"] = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=tzutc())
                    trace.append(event)
            log.append(trace)
    return log


def write_to_xes(frequencies, path):
    model = generate_pm4py_log(trace_frequencies=frequencies)
    xes_exporter.apply(model, path)


def write_to_csv(frequencies, path):
    f = open(path, "w+")
    f.write("Case ID;Activity\n")
    case = 0
    for entry in frequencies.items():
        frequency = entry[1]
        activities = list(filter(None, entry[0].split(EVENT_DELIMETER)))
        for i in range(0, frequency):
            time = 0
            for activity in activities:
                if TRACE_END not in activity:
                    f.write(str(case) + ";" + str(activity) + "\n")
                    time += 1
            case += 1
    f.flush()
    f.close()


main()