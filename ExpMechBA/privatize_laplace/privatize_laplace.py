from opyenxes.classification.XEventNameClassifier import XEventNameClassifier
import numpy as np

TRACE_START = "TRACE_START"
TRACE_END = "TRACE_END"
EVENT_DELIMETER = ">>>"


def privatize_tracevariants(log, epsilon, P, N):
    # transform log into event view and get prefix frequencies
    event_int_mapping = create_event_int_mapping(log)
    print("Retrieving true prefix frequencies", end='')
    known_prefix_frequencies = get_prefix_frequencies_from_log(log)
    events = list(event_int_mapping.keys())
    events.remove(TRACE_START)

    final_frequencies = {}
    trace_frequencies = {"": 0}
    for n in range(1, N + 1):
        # get prefix_frequencies, using either known frequency, or frequency of parent, or 0
        trace_frequencies = get_prefix_frequencies_length_n(trace_frequencies, events, n, known_prefix_frequencies)
        # laplace_mechanism
        trace_frequencies = apply_laplace_noise_tf(trace_frequencies, epsilon)

        # prune
        if n < N:
            trace_frequencies = prune_trace_frequencies(trace_frequencies, P)
        # print(trace_frequencies)
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
        # print(trace_frequencies)
        # print(n)
    return final_frequencies


def create_event_int_mapping(log):
    classifier = XEventNameClassifier()
    event_name_list = []
    for trace in log[0]:
        for event in trace:
            event_name = classifier.get_class_identity(event)
            if not str(event_name) in event_name_list:
                event_name_list.append(event_name)
    event_int_mapping = {}
    event_int_mapping[TRACE_START] = 0
    current_int = 1
    for event_name in event_name_list:
        event_int_mapping[event_name] = current_int
        current_int = current_int + 1
    event_int_mapping[TRACE_END] = current_int
    return event_int_mapping


def get_prefix_frequencies_from_log(log):
    classifier = XEventNameClassifier()
    prefix_frequencies = {}
    for trace in log[0]:
        current_prefix = ""
        for event in trace:
            current_prefix = current_prefix + classifier.get_class_identity(event) + EVENT_DELIMETER
            if current_prefix in prefix_frequencies:
                frequency = prefix_frequencies[current_prefix]
                prefix_frequencies[current_prefix] += 1
            else:
                prefix_frequencies[current_prefix] = 1
        current_prefix = current_prefix + TRACE_END
        if current_prefix in prefix_frequencies:
            frequency = prefix_frequencies[current_prefix]
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


def prune_trace_frequencies(trace_frequencies, P):
    pruned_frequencies = {}
    for entry in trace_frequencies.items():
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


def apply_laplace_noise_tf(trace_frequencies, epsilon):
    lambd = 1 / epsilon
    for trace_frequency in trace_frequencies:
        noise = int(np.random.laplace(0, lambd))
        trace_frequencies[trace_frequency] = trace_frequencies[trace_frequency] + noise
        if trace_frequencies[trace_frequency] < 0:
            trace_frequencies[trace_frequency] = 0
    return trace_frequencies

