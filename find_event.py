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

"""
var array
0: scaling       | Scales the output of the analysis function                    | Used to invert small values
1: min value     | Minimum value of analysis function to accept input event      | Takes effect after scaling
2: max value     | Maximum value of analysis function to accept input event      | Takes effect after scaling
3: start         | Start point of analysis in Event
4: end           | End point of analysis in Event
5: var 1         | Depending of analysis function
6: var 2         | Depending of analysis function
"""

def find_event(
    file,
    funk:list() = [],
    funk_var:list[list[int]] = [[]],
    minfit: float = 0,
    include_channel: list[str] = ["OB-01","OB-02"],
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
            fit = 0
            
            for num,fun in enumerate(funk):
                val = fun(lh5_obj.nda[0],funk_var[num]) /funk_var[num][0]
                if (val >= funk_var[num][1] and val <= funk_var[num][2]):
                    fit += val
                else:
                    continue          
            if (fit > minfit):
                fitness.append(fit)
                event.append(entry)
        channel_fitness.append(fitness)
        event_list.append(event)
        
    return channel_fitness,event_list
        
# Funktions for find_event
#returns the average of the event
def average(
    data: np.ndarray,
    var: list,
    ):
    data = data[var[3]:var[4]]
    return np.average(data)

#returns the first absolute maxiumum of the event
def max_val(
    data: np.ndarray,
    var: list,
):
    data = data[var[3]:var[4]]    
    maxi = np.nanmax(data)
    if isinstance(maxi, list):
        return maxi[0]
    else:
        return maxi
    
#returns the first absolute miniumum of the event
def min_val(
    data: np.ndarray,
    var: list,
):
    data = data[var[3]:var[4]]
    data = data[var[3]:var[4]]    
    mini = np.nanmin(data)
    if isinstance(mini, list):
        return mini[0]
    else:
        return mini

#shows the length of a series of event data (to help selection a range for the functions before)
def event_length(
    file: str,
    channel_data_dir: str,
    event: int = 0,
    read_length: int = 10,
):
    for lh5_obj, entry, n_rows in LH5Iterator(file, channel_data_dir ,buffer_len=1):
        print(len(lh5_obj.nda[0]))
        if entry >= read_length:
            break

#shows the "metadata" from a array of events
def print_event_data(
    file: str,
    event: list[int] = [0,1],
    cols: list[str]= ["eventnumber","baseline","channel","deadtime","runtime","timestamp",],
    include_channel: list[str] = ["OB-01"],
    data_dir: str = "/raw",
    
):
    #creates dictionary and selects channels form input channel names
    cmap = open("/mnt/atlas01/projects/legend/data/com/raw/2022-04-13-sipm-test/channel-map.json")
    channel_map = json.load(cmap)
    channel_dict = {}
    for i in channel_map["hardware_configuration"]["channel_map"]:
        channel_dict[channel_map["hardware_configuration"]["channel_map"][i]["det_id"]] = i
    channel_data_dir=[channel_dict[i]+data_dir for i in include_channel]
    
    pd.options.display.precision = 18
    c = 0
    for i,cdd in enumerate(channel_data_dir):
        for j in event:
            obj, n_rows = store.read_object(cdd, file, start_row=j, n_rows=1)
            if c == 0:
                c = 1
                data = obj.get_dataframe(cols)
            else:
                data = pd.concat([data,obj.get_dataframe(cols)],ignore_index=True)
    display(data)
    
"""
└── raw
    ├── baseline · array<1>{real}
    ├── channel · array<1>{real}
    ├── daqenergy · array<1>{real}
    ├── deadtime · array<1>{real}
    ├── dr_maxticks · array<1>{real}
    ├── dr_start_pps · array<1>{real}
    ├── dr_start_ticks · array<1>{real}
    ├── dr_stop_pps · array<1>{real}
    ├── dr_stop_ticks · array<1>{real}
    ├── eventnumber · array<1>{real}
    ├── numtraces · array<1>{real}
    ├── packet_id · array<1>{real}
    ├── runtime · array<1>{real}
    ├── timestamp · array<1>{real}
    ├── to_abs_mu_usec · array<1>{real}
    ├── to_dt_mu_usec · array<1>{real}
    ├── to_master_sec · array<1>{real}
    ├── to_mu_sec · array<1>{real}
    ├── to_mu_usec · array<1>{real}
    ├── to_start_sec · array<1>{real}
    ├── to_start_usec · array<1>{real}
    ├── tracelist · array<1>{array<1>{real}}
    │   ├── cumulative_length · array<1>{real}
    │   └── flattened_data · array<1>{real}
    ├── ts_maxticks · array<1>{real}
    ├── ts_pps · array<1>{real}
    ├── ts_ticks · array<1>{real}
    └── waveform · table{t0,dt,values}
"""