from opyenxes.data_in.XUniversalParser import XUniversalParser
from opyenxes.classification.XEventNameClassifier import XEventNameClassifier
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log import log as event_log
import datetime
from dateutil.tz import tzutc

from privatize_laplace import privatize_df_laplace

TRACE_START = "TRACE_START"
TRACE_END = "TRACE_END"
EVENT_DELIMETER = ">>>"

P = 2
P_smart = 2
N = 9

basePath = '/Users/stephan/SaCoFa_EventLogs'          # path to the folder containing all the event logs
logName = 'CoSeLoG'                             # the preferrable file structure is given in the README

inPath = basePath + '/Logs/' + logName + '.xes'
epsRange = [1.0]            # range of epsilon
tries = 10
#modeRange = ['laplace','ba','ba_prune','ba']
#modeRange = ['ba','laplace','occured','ba_prune']
modeRange = ['ba_prune']
#modeRange = ['occured','ba',','ba_prune','ba_prune_multi']


def main():
    log_x, log_pm4py = readLogFile(inPath)
    epsilon = 1.0
    private_log = privatize_df_laplace.privatize_tracevariants(log_x, log_pm4py, epsilon)
    print(private_log)
    print("Done for all eps for all tries.")


def readLogFile(file):
    with open(file) as log_file:
        return XUniversalParser().parse(log_file), xes_importer.apply(file)


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