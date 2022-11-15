import os, json
import pygama.lgdo.lh5_store as lh5
from pygama.lgdo import LH5Iterator
import numpy as np
import pandas as pd
import matplotlib as plt
from pygama.lgdo.lh5_store import show
from pygama.lgdo.lh5_store import ls


#file = "/mnt/atlas01/users/shofinger/dsp_7/a/113433.lh5"

store=lh5.LH5Store()

def nofunk(
    data: np.ndarray,
    var: list,
    ):
    return 0

"""
var array
0: scaling
1: start
2: end
"""

def find_event(
    file,
    funk1 = nofunk,
    funk1_var = [1],
    funk2 = nofunk,
    funk2_var = [1],
    funk3 = nofunk,
    funk3_var = [1],
    include_channel: list[str] = ["OB-01"],
    data_dir: str = "/raw/waveform/values",
    simul_process: int = 1, 
    
    ):
    
    #creates dictionary and selects channels form input channel names
    cmap = open("/mnt/atlas01/projects/legend/data/com/raw/2022-04-13-sipm-test/channel-map.json")
    channel_map = json.load(cmap)
    channel_dict = {}
    for i in channel_map["hardware_configuration"]["channel_map"]:
        channel_dict[channel_map["hardware_configuration"]["channel_map"][i]["det_id"]] = i
    channel_data_dir=[channel_dict[i]+data_dir for i in include_channel]
    
    #itterate throu channels and events
    channel_fitness = []
    event_list = []
    for i,cdd in enumerate(channel_data_dir):
        fitness = []
        event = []
        for lh5_obj, entry, n_rows in LH5Iterator(file, cdd ,buffer_len=1):
            #print(f"entry {entry}, energy = {lh5_obj} ({n_rows} rows)") #do not run it with buffer_len=1
            fitness.append(funk1(lh5_obj.nda[0],funk1_var) /funk1_var[0])
            fitness[entry] += funk2(lh5_obj.nda[0],funk2_var) /funk2_var[0]
            fitness[entry] += funk3(lh5_obj.nda[0],funk3_var) /funk3_var[0]
            event.append(entry)
        channel_fitness.append(fitness)
        event_list.append(event)
    return channel_fitness,event_list
        
    
def median(
    data: np.ndarray,
    var: list,
    ):
    data = data[var[1]:var[2]]
    return np.average(data)

