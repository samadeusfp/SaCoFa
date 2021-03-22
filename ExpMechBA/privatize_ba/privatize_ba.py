from opyenxes.classification.XEventNameClassifier import XEventNameClassifier
import numpy as np
import random
import sys
from privatize_occured import exp_mech as exp
from privatize_ba import behavioralAppropriateness as ba

TRACE_START = "TRACE_START"
TRACE_END = "TRACE_END"
EVENT_DELIMETER = ">>>"

activityKey = 'Activity'


def privatize_tracevariants(log, epsilon, P, N,smart_pruning=False, P_smart=0,sensitivity=1):
    epsilon = epsilon/sensitivity
    if not smart_pruning:
        P_smart = P
    print("Retrieving behavioral appropriateness relations")
    traces = get_traces_from_log(log=log[0])
    events = get_events_from_traces(traces)
    followsRelations, precedesRelations = ba.getBARelations(traces=traces, events=events)
    events.append(TRACE_END)        # TRACE_END is not relevant for follows/precedes relations, but is later used to generate new prefix variants

    print("Retrieving true prefix frequencies")
    known_prefix_frequencies = get_prefix_frequencies_from_log(log=log)

    print("Sanitizing...")
    final_frequencies = {}
    trace_frequencies = {"": 0}
    for n in range(1, N + 1):
        # get prefix_frequencies, using either known frequency, or frequency of parent, or 0
        trace_frequencies = get_prefix_frequencies_length_n(trace_frequencies, events, n, known_prefix_frequencies)
        # exp_mech
        trace_frequencies, conformASet = privatize_trace_variants(trace_frequencies=trace_frequencies, epsilon=epsilon,
                                                     followRelations=followsRelations,
                                                     precedesRelations=precedesRelations, allEvents=events,
                                                     allTraces=traces, sensitivity=sensitivity)
        # prune
        if n < N:
            trace_frequencies = prune_trace_frequencies(trace_frequencies, P, P_smart, conformASet)

        # add finished traces to output, remove from list, sanity checks
        new_frequencies = {}
        for entry in trace_frequencies.items():
            if TRACE_END in entry[0]:
                final_frequencies[entry[0]] = entry[1]
            elif n == N:
                final_frequencies[entry[0][:-3]] = entry[1]
            else:
                new_frequencies[entry[0]] = entry[1]
        trace_frequencies = new_frequencies

    return final_frequencies


def get_prefix_frequencies_from_log(log):
    classifier = XEventNameClassifier()
    prefix_frequencies = {}
    for trace in log[0]:
        current_prefix = ""
        for event in trace:
            current_prefix = current_prefix + classifier.get_class_identity(event) + EVENT_DELIMETER
            if current_prefix in prefix_frequencies:
                prefix_frequencies[current_prefix] += 1
            else:
                prefix_frequencies[current_prefix] = 1
        current_prefix = current_prefix + TRACE_END
        if current_prefix in prefix_frequencies:
            prefix_frequencies[current_prefix] += 1
        else:
            prefix_frequencies[current_prefix] = 1
    return prefix_frequencies


def get_prefix_frequencies_length_n(trace_frequencies, events, n, known_prefix_frequencies):
    prefixes_length_n = {}
    for prefix, frequency in trace_frequencies.items():
        for new_prefix in pref(prefix, events, n):
            if new_prefix in known_prefix_frequencies:
                new_frequency = known_prefix_frequencies[new_prefix]
                prefixes_length_n[new_prefix] = new_frequency
            else:
                prefixes_length_n[new_prefix] = 0
    return prefixes_length_n


def privatize_trace_variants(trace_frequencies, epsilon, followRelations, precedesRelations, allEvents, allTraces,sensitivity):
    conformsToBASet = []
    violatesBASet = dict()
    firstEvents = get_first_events(traceSet=allTraces)         # all events which appear as the first event in a trace in the original log
    for trace_frequency in trace_frequencies.items():
        working_trace_frequency = list(filter(None, trace_frequency[0].split(EVENT_DELIMETER)))

        if len(working_trace_frequency) == 1:                   # len(prefix) == 1 -> does a trace which begins with this prefix/event exist in the original log?
            if working_trace_frequency[0] in firstEvents:       # if so, this prefix conforms to BA, if not BA is violated
                conformsToBASet.append(trace_frequency[0])
            else:
                violatesBASet[trace_frequency[0]] = 1
            continue

        baViolations = ba.getBAViolations(allEvents=allEvents, followsRelations=followRelations, precedesRelations=precedesRelations, prefix=working_trace_frequency, TRACE_END=TRACE_END)
        if baViolations == 0:
            conformsToBASet.append(trace_frequency[0])
        else:
            violatesBASet[trace_frequency[0]] = baViolations

    not_to_prune_prefix = conformsToBASet.copy()

    output_universes = np.linspace(0, len(violatesBASet), num=len(violatesBASet)+1, dtype=int)
    chosen_universe = exp.exp_mech(output_universes, epsilon)
    # print("conformsToBASet: ", len(conformsToBASet), "| violatesBASet: ", len(violatesBASet), "| chosen universe: ",
    #        chosen_universe)

    while chosen_universe > 0:
        for x in random.sample(violatesBASet.keys(), 1):
            chosen_universe = chosen_universe - min(violatesBASet[x],sensitivity)
            conformsToBASet.append(x)
            violatesBASet.pop(x)
    return apply_laplace_noise_tf(trace_frequencies, conformsToBASet, epsilon), not_to_prune_prefix


def get_first_events(traceSet):
    firstEvents = list()
    for trace in traceSet:
        if trace[0] not in firstEvents:
            firstEvents.append(trace[0])

    return firstEvents


def get_traces_from_log(log):
    classifier = XEventNameClassifier()
    traces = list()
    for trace in log:
        decoded_trace = list()
        for event in trace:
            decoded_trace.append(classifier.get_class_identity(event))

        traces.append(decoded_trace)

    return traces


def get_events_from_traces(traceSet):
    events = list()
    for t in traceSet:
        for e in t:
            if e not in events:
                events.append(e)

    return events


def prune_trace_frequencies(trace_frequencies, P,P_smart,conformSet):
    pruned_frequencies = {}
    for entry in trace_frequencies.items():
        if entry[0] in conformSet:
            if entry[1] >= P_smart or TRACE_END in entry[0]:
                pruned_frequencies[entry[0]] = entry[1]
        else:
            if entry[1] >= P or TRACE_END in entry[0]:
                pruned_frequencies[entry[0]] = entry[1]
    return pruned_frequencies


def pref(prefix, events, n):
    prefixes_length_n = []
    if not TRACE_END in prefix:
        for event in events:
            current_prefix = ""
            if event == TRACE_END:
                current_prefix = prefix + event
            else:
                current_prefix = prefix + event + EVENT_DELIMETER
            prefixes_length_n.append(current_prefix)
    return prefixes_length_n


def apply_laplace_noise_tf(trace_frequencies, conformsToBASet, epsilon):
    lambd = 1 / epsilon
    for trace_frequency in conformsToBASet:
        noise = int(np.random.laplace(0, lambd))
        trace_frequencies[trace_frequency] = trace_frequencies[trace_frequency] + noise
        if trace_frequencies[trace_frequency] < 0:
            trace_frequencies[trace_frequency] = 0
    return trace_frequencies