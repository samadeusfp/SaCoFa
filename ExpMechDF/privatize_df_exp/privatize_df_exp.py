import matplotlib.pyplot as plt
import sys
import sqlite3
import os
import subprocess
import requests
import time
import urllib3
import shutil
import glob
from tabulate import tabulate
import pathlib
from pathlib import Path
from opyenxes.classification.XEventNameClassifier import XEventNameClassifier
from opyenxes.data_in.XUniversalParser import XUniversalParser
#import opyenxes.factory.XFactory as xfactory
import numpy as np
import pandas as pd
from pm4py.objects.log import log as event_log
from pm4py.objects.log.importer.xes import importer as xes_import_factory
from pm4py.objects.log import util as log_utils
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
import random
import datetime
from dateutil.tz import tzutc
from collections import Counter as Counter
from privatize_df_ba import exp_mech as exp



TRACE_START = "TRACE_START"
TRACE_END = "TRACE_END"
EVENT_DELIMETER = ">>>"

sys.setrecursionlimit(1000)
def split_df_relations(k_follows_relations, event_int_mapping,max_k):
    add_noise_set=[]
    no_noise_set=[]
    for i in range(0, len(event_int_mapping)-1):
        for j in range(1, len(event_int_mapping)):
            if i == event_int_mapping[TRACE_START] and j == event_int_mapping[TRACE_END]:
                pass
            elif k_follows_relations[i][j] > max_k:
                no_noise_set.append((i,j))
            else:
                add_noise_set.append((i,j))
    print("Add Noise Set: " + str(len(add_noise_set)))
    print("No Noise Set: " + str(len(no_noise_set)))
    return add_noise_set, no_noise_set


def privatize_df_frequencies(df_relations, event_int_mapping, epsilon,k_follows_relations,max_k):
    add_noise_set, no_noise_set = split_df_relations(k_follows_relations, event_int_mapping,max_k)
    output_universes = np.linspace(0,len(no_noise_set), num=len(no_noise_set)+1, dtype=int)
    chosen_universe = exp.exp_mech(output_universes, epsilon)
    for x in random.sample(no_noise_set, chosen_universe):
        add_noise_set.append(x)
        no_noise_set.remove(x)
    return apply_laplace_noise_df(df_relations, add_noise_set, epsilon)

def privatize_df(log, event_int_mapping, epsilon,k_follows_relations,max_k):
    #get true df frequencies
    print("Retrieving Directly Follows Frequencies   ", end = '')
    df_relations = get_df_frequencies(log, event_int_mapping)

    traces_before = np.sum(df_relations[0])
    print("\n Traces before noise:", np.sum(df_relations[0]),"\n")

    print("Done")
    #privatize df frequencies
    print("Privatizing Log   ", end = '')
    int_event_mapping = {value:key for key, value in event_int_mapping.items()}
    activity_list = []
    for key, value in int_event_mapping.items():
        temp = [key,value]
        activity_list.append(value)

    #df = pd.DataFrame(data=df_relations, index=activity_list, columns=activity_list)
    #df.to_csv('df_relations.csv',sep=',',columns=activity_list, header=activity_list)
    #print(int_event_mapping)
    df_relations = privatize_df_frequencies(df_relations, event_int_mapping, epsilon,k_follows_relations,max_k)
    print("Done")

    #write to disk
    print("Writing privatized Directly Follows Frequencies to disk   ","\n")
    #write_to_dfg(df_relations, event_int_mapping, output)
    private_log, counter, total_df_amount, total_df_deleted = generate_pm4py_log(df_relations, event_int_mapping,int_event_mapping, activity_list)
    ##############xes_exporter.export_log(private_log,output)
    print("Done")
    return private_log, traces_before, counter, total_df_amount, total_df_deleted

def create_event_int_mapping(log):
    event_name_list=[]
    #print("\n log type:",type(log))
    for trace in log:
        #print("trace type:",type(trace))
        for event in trace:
            #print("event type:",type(event), event)
            event_name = event["concept:name"]
            if not str(event_name) in event_name_list:
                event_name_list.append(event_name)
    event_int_mapping={}
    event_int_mapping[TRACE_START]=0
    current_int=1
    for event_name in event_name_list:
        event_int_mapping[event_name]=current_int
        current_int=current_int+1
    event_int_mapping[TRACE_END]=current_int
    #print("\n",type(event_int_mapping)," \n",event_int_mapping,"\n \n")
    return event_int_mapping

def get_df_frequencies(log, event_int_mapping):
    classifier = XEventNameClassifier()
    df_relations = np.zeros((len(event_int_mapping),len(event_int_mapping)), dtype=int)
    for trace in log[0]:
        current_event = TRACE_START
        for event in trace:
            next_event = classifier.get_class_identity(event)
            current_event_int = event_int_mapping[current_event]
            next_event_int = event_int_mapping[next_event]
            df_relations[current_event_int, next_event_int] += 1
            current_event = next_event

        current_event_int = event_int_mapping[current_event]
        next_event = TRACE_END
        next_event_int = event_int_mapping[next_event]
        df_relations[current_event_int, next_event_int] += 1


    return df_relations

def apply_laplace_noise_df(df_relations, non_zero_set, epsilon):
    lambd = 1/epsilon
    for cell in non_zero_set:
        a = cell[0]
        b = cell[1]
        noise = int(np.random.laplace(0, lambd))
        df_relations[a,b] = df_relations[a,b] + noise
        if df_relations[a,b]<0:
            df_relations[a,b]=0
    return df_relations

def write_to_dfg(df_relations, event_int_mapping, output):
    out=output+".dfg"
    print("\n output_path: ",out,"\n")
    f = open(out,"w+")
    f.write(str(len(df_relations)-2)+"\n")
    for key in event_int_mapping:
        if not (str(key)==TRACE_START or str(key)==TRACE_END):
            f.write(str(key)+"\n")

    #starting activities
    no_starting_activities=0
    starting_frequencies=[]
    for x in range(1,len(df_relations)):
        current = df_relations[0,x]
        if current!=0:
            no_starting_activities+=1
            starting_frequencies.append((x-1,current))
    f.write(str(no_starting_activities)+"\n")
    for x in starting_frequencies:
        f.write(str(x[0])+"x"+str(x[1])+"\n")

    #ending activities
    no_ending_activities=0
    ending_frequencies=[]
    for x in range(0,len(df_relations)-1):
        current = df_relations[x,len(df_relations)-1]
        if current!=0:
            no_ending_activities+=1
            ending_frequencies.append((x-1, current))
    f.write(str(no_ending_activities)+"\n")
    for x in ending_frequencies:
        f.write((str(x[0])+"x"+str(x[1])+"\n"))

    #df relations
    for x in range(1,len(df_relations)-1):
        for y in range(1,len(df_relations)-1):
            if df_relations[x,y]!=0:
                f.write(str(x-1)+">"+str(y-1)+"x"+str(df_relations[x,y])+"\n")
    f.close

def find_path(df_relations,deleted_df,activity_list,possible_elements,existing_path,depth):

    current_activity = existing_path[-1]
    full_trace = False
    if current_activity == df_relations.shape[0]-1:
        full_trace = True
    if full_trace==False:
        if np.sum(df_relations[current_activity]) > 0:

            ###statistic choice
            probabilities_current_df = df_relations[current_activity] / np.sum(df_relations[current_activity])

            ###equeal probability
            #probabilities_current_df = np.clip(df_relations[current_activity], 0, 1)* (1/np.count_nonzero(df_relations[current_activity]))
            ###
            next_activity = np.random.choice(possible_elements,p=probabilities_current_df)
            existing_path.append(next_activity)
            if df_relations[existing_path[-2],existing_path[-1]] > 0:
                df_relations[existing_path[-2],existing_path[-1]] -= 1
            depth += 1
            if depth == 500:
                print("depth over 500",existing_path)
                print(df_relations)
                return [0]
            existing_path=find_path(df_relations,deleted_df,activity_list,possible_elements,existing_path,depth)
        else:
            deleted_df[:,existing_path[-1]] = df_relations[:,existing_path[-1]]
            #print(df_relations,"\n")
            #print(deleted_df,"\n")

            #df = pd.DataFrame(data=df_relations, index=activity_list, columns=activity_list)
            #df.to_csv('df_relation_end.csv',sep=',',columns=activity_list, header=activity_list)

            #df = pd.DataFrame(data=deleted_df, index=activity_list, columns=activity_list)
            #df.to_csv('df_deletions_end.csv',sep=',',columns=activity_list, header=activity_list)

            #df = pd.DataFrame(data=df_relations, index=activity_list, columns=activity_list)
            #df.to_csv('df_relations_noised.csv',sep=',',columns=activity_list, header=activity_list)
            #sys.exit()
            if current_activity == 0:
                print("No more viable paths to TRACE_END")
                return [0]
            depth += 1
            df_relations[:,existing_path[-1]] = 0
            existing_path = existing_path[:-1]
            existing_path = find_path(df_relations,deleted_df,activity_list,possible_elements,existing_path,depth)


    return existing_path

def generate_pm4py_log(df_relations, event_int_mapping,int_event_mapping, activity_list):
    #int_event_mapping = {value:key for key, value in event_int_mapping.items()}
    #print(int_event_mapping)

    log = event_log.EventLog()
    size = df_relations.shape[0]-1
    print("START:",np.sum(df_relations[0]),np.sum(df_relations,axis=0)[size],"\n\n")
    trace_amount = min(np.sum(df_relations[0]),np.sum(df_relations,axis=0)[size])
    possible_elements = list(range(0,size+1))#counter < trace_amount
    total_df_amount = df_relations.sum()
    deleted_df = np.zeros((len(int_event_mapping),len(int_event_mapping)), dtype=int)
    new_df_amount = df_relations.sum()

    #df = pd.DataFrame(data=df_relations, index=activity_list, columns=activity_list)
    #df.to_csv('df_relations_noised.csv',sep=',',columns=activity_list, header=activity_list)

    #print(tabulate(df, headers= activity_list,tablefmt = 'pretty'))
    #plt.matshow(df_relations,fignum=None,cmap='gray')
    #plt.savefig('df_relations.png',dpi=300)
    #print("hello?")
    #sys.exit()
    counter = 0
    while(True):
        empty_list=[0]
        old_df_amount = new_df_amount
        next_trace = find_path(df_relations,deleted_df,activity_list,possible_elements ,empty_list,0)
        new_df_amount = df_relations.sum()

        #print("trace nr.: ",counter,next_trace,"lentgh:",len(next_trace))
        #print("total dfs - current trace:", old_df_amount - new_df_amount)

        #if old_df_amount - new_df_amount != len(next_trace) -1:
        #    print("weird deletion")
        #sys.exit()
        if len(next_trace) <= 1:
            print("All traces attached to log.", counter, "traces")
            break

        trace = event_log.Trace()
        trace.attributes["concept:name"] = counter
        counter += 1


        for i in range(len(next_trace)-1):
            #print(df_relations[next_trace[i],next_trace[i+1]])
            #if df_relations[next_trace[i],next_trace[i+1]] > 0:
            #    df_relations[next_trace[i],next_trace[i+1]] -= 1
            if str(int_event_mapping[next_trace[i]]) == TRACE_START:
                continue
            event = event_log.Event()
            event["concept:name"] = str(int_event_mapping[next_trace[i]])
            event["time:timestamp"] = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=tzutc())
            trace.append(event)

        log.append(trace)
        #print("appended:" ,counter, next_trace)

    #print(df_relations,"\n")
    #print("deleted df:\n",deleted_df,"\n")

    #df = pd.DataFrame(data=df_relations, index=activity_list, columns=activity_list)
    #df.to_csv('df_relation_end.csv',sep=',',columns=activity_list, header=activity_list)

    df_deletions = np.add(deleted_df,df_relations)
    #print(df_deletions,"\n")

    #df = pd.DataFrame(data=df_deletions, index=activity_list, columns=activity_list)
    #df.to_csv('df_deletions_end.csv',sep=',',columns=activity_list, header=activity_list)

    total_df_deleted = df_deletions.sum()
    print("total cases:",counter)
    print("Total df relations:",total_df_amount,"total deletions:",total_df_deleted," Percentage deleted =", total_df_deleted / total_df_amount)
    return log, counter, total_df_amount, total_df_deleted

def get_prefix_frequencies_from_log(log):
        prefix_frequencies = {}
        for trace in log:
            current_prefix = ""
            for event in trace:
                #current_prefix = current_prefix + event["concept:name"] + EVENT_DELIMETER
                current_prefix = current_prefix + event["concept:name"] + EVENT_DELIMETER
                #if current_prefix in prefix_frequencies:
                #    frequency = prefix_frequencies[current_prefix]
                #    prefix_frequencies[current_prefix] += 1
                #else:
                #    prefix_frequencies[current_prefix] = 1
            current_prefix = current_prefix + TRACE_END
            #prefix_frequencies[current_prefix] = 1
            if current_prefix in prefix_frequencies:
                frequency = prefix_frequencies[current_prefix]
                prefix_frequencies[current_prefix] += 1
            else:
                prefix_frequencies[current_prefix] = 1
        return prefix_frequencies

def get_k_follows_trace(activity_list):
    k_follows_trace = dict()
    counter_outer_loop= 0
    for a in activity_list[:-1]:
        k_follows_trace[a] = dict()
        counter_inner_loop = 0
        for b in activity_list:
            if counter_inner_loop != counter_outer_loop and counter_inner_loop > counter_outer_loop:
                k_follows_trace[a][b] = counter_inner_loop - counter_outer_loop
            counter_inner_loop +=1
        counter_outer_loop += 1
    return k_follows_trace

def init_k_follows_relation(event_mapping):
    k_follows_relations = dict()
    for a in range(0, len(event_mapping)):
        k_follows_relations[a] = dict()
        for b in range(0, len(event_mapping)):
            k_follows_relations[a][b] = sys.maxsize
    return k_follows_relations

def update_k_follows(k_follows_relations,k_follows_trace,int_event_mapping):
    for activity_a in k_follows_trace.keys():
        for activity_b in k_follows_trace[activity_a].keys():
            k_follows_relations[int_event_mapping[activity_a]][int_event_mapping[activity_b]] = min(k_follows_relations[int_event_mapping[activity_a]][int_event_mapping[activity_b]],k_follows_trace[activity_a][activity_b])
    return k_follows_relations


def get_k_follows_relations(log,event_mapping):
    k_follows_relations = init_k_follows_relation(event_mapping)
    for trace in log:
        activity_list = list()
        activity_list.append(TRACE_START)
        for event in trace:
            activity_list.append(event["concept:name"])
        activity_list.append(TRACE_END)
        k_follows_trace = get_k_follows_trace(activity_list)
        k_follows_relations = update_k_follows(k_follows_relations,k_follows_trace,event_mapping)
    print(k_follows_relations)
    return k_follows_relations

def privatize_tracevariants(log_x,log_pm4py,epsilon,max_k):
    start = time.time()
    column_names = ['epsilon', 'traces_before', 'traces_after', 'total_df_amount', 'total_df_deleted',
                    'df_percentage deleted', 'variants_before', 'variants_after', 'common_variants', 'runtime']
    stats_dataframe = pd.DataFrame(columns=column_names)

    prefix = get_prefix_frequencies_from_log(log_pm4py)
    event_mapping = create_event_int_mapping(log_pm4py)

    trace_variants = Counter(prefix)
    most_common_tv_list = trace_variants.most_common(20)

    common_traces_dict = dict(most_common_tv_list)
    common_traces_dict['epsilon'] = 99.9

    column_names_common_tv = list(common_traces_dict.keys())

    trace_variant_df = pd.DataFrame(columns=column_names_common_tv)
    trace_variant_df = trace_variant_df.append(common_traces_dict, ignore_index=True)

    k_follows_relations = get_k_follows_relations(log_pm4py,event_mapping)

    private_log, traces_before, traces_after, total_df_amount, total_df_deleted = privatize_df(log_x, event_mapping,epsilon,k_follows_relations,max_k)
    end = time.time()
    df_percentage_deleted = total_df_deleted / total_df_amount

    prefix_after = get_prefix_frequencies_from_log(private_log)
    comkeys = prefix.keys() & prefix_after.keys()

    stats_dataframe = stats_dataframe.append(
        {'epsilon': epsilon, 'traces_before': traces_before, 'traces_after': traces_after,
         'total_df_amount': total_df_amount, 'total_df_deleted': total_df_deleted,
         'df_percentage deleted': df_percentage_deleted, 'variants_before': len(prefix.keys()),
         'variants_after': len(prefix_after.keys()), 'common_variants': len(comkeys), 'runtime': end - start},
        ignore_index=True)

    return private_log




