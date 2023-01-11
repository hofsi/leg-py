import os, json
import pygama.lgdo.lh5_store as lh5
from pygama.lgdo import LH5Iterator
from pygama.lgdo import LH5Store
import numpy as np
import pandas as pd
import matplotlib as plt
from pygama.lgdo.lh5_store import show
from pygama.lgdo.lh5_store import ls
import multiprocessing


#file = "/mnt/atlas01/users/shofinger/dsp_7/a/113433.lh5"

store=lh5.LH5Store()

"""
var array
0: scaling       | Scales the output of the analysis function                    | Used to invert small values
1: min value     | Minimum value of analysis function to accept input event      | Takes effect after scaling     DEACTIVATED
2: max value     | Maximum value of analysis function to accept input event      | Takes effect after scaling     DEACTIVATED
3: start         | Start point of analysis in Event
4: end           | End point of analysis in Event
5: var 1         | Depending of analysis function
6: var 2         | Depending of analysis function
"""
def channel_itterator(
    file_entry,
    channel_data_dir,
    funk,
    funk_var,
    minfit,
    q,
    calibration,
    include_channel,
):
    #calculates fittness for each channel and event
    event_fitness = []
    event_nr = []
  
    for i,cdd in enumerate(channel_data_dir):

        fitness = []
        nr = []

        obj = store.read_object(cdd[0:10] + "baseline",file_entry)[0]      
        for lh5_obj, entry, n_rows in LH5Iterator(file_entry, cdd ,buffer_len=100):
            #print(f"entry {entry}, energy = {lh5_obj} ({n_rows} rows)") #do not run it with buffer_len=1
            for a in range(n_rows):
                fit = 0
                for num,fun in enumerate(funk):                   
                    fit += fun(lh5_obj.nda[a],funk_var[num],obj.nda[entry+a]) /funk_var[num][0] / (calibration[include_channel[i]][1][1] - calibration[include_channel[i]][0][1])
                fitness.append(fit)
                nr.append(entry+a)  
        event_fitness.append(fitness)
        event_nr.append(nr)
    channel_fitness = []
    
    for i in range(len(event_fitness[0])):
        fit = 0
        for j in range(len(event_fitness)):
            fit += event_fitness[j][i]
        if fit > minfit:
            channel_fitness.append((fit,event_nr[0][i]))
    
    q.put(sorted(channel_fitness,reverse=True))
    


def find_event(
    file_list:list[str],
    funk:list = [],
    funk_var:list[list[int]] = [[]],
    minfit: float = 0,                                                 #is scalled by the ammount of channels
    include_channel: list[str] = ["OB-01","OB-02","OB-03","OB-05","OB-06","OB-07","OB-08","OB-09","OB-12","OB-13","OB-14","OB-17","OB-21","OB-22","OB-23","OB-24","OB-25","OB-26","OB-28","OB-29","OB-31","OB-35","OB-36","OB-37","OB-38","OB-39","OB-40"],
    data_dir: str = "/raw/waveform/values",
    calibration_file: str = "calibration_data_231824"
    
    ):

    #creates dictionary and selects channels form input channel names
    cmap = open("/mnt/atlas01/projects/legend/data/com/raw/2022-04-13-sipm-test/channel-map.json")
    channel_map = json.load(cmap)
    channel_dict = {}
    for i in channel_map["hardware_configuration"]["channel_map"]:
        channel_dict[channel_map["hardware_configuration"]["channel_map"][i]["det_id"]] = i
        
    channel_data_dir=[channel_dict[i]+data_dir for i in include_channel]
    
    
    with open(calibration_file, 'r') as openfile:
        calibration = json.load(openfile)
    
    channel_name_list = [channel_map["hardware_configuration"]["channel_map"][i]["det_id"] for i in channel_map["hardware_configuration"]["channel_map"]]
 
    fittnes_dict = {}
    ctx = multiprocessing.get_context('spawn')
    q = []
    process = []
    for i,file_entry in enumerate(file_list):
        q.append(ctx.Queue())
        process.append(multiprocessing.Process(target=channel_itterator,args=(file_entry,channel_data_dir,funk,funk_var,minfit,q[i],calibration,include_channel)))
        process[i].start()
    
    for i,file_entry in enumerate(file_list):
        fittnes_dict[file_entry] = q[i].get()
        process[i].join()
        print("Process for "+ str(file_entry)+ " has finished" )
        
    return fittnes_dict
        
# Funktions for find_event
#returns the average of the event
def average(
    data: np.ndarray,
    var: list,
    baseline: float,
    ):
    data = data[var[3]:var[4]]
    return (np.average(data,returned=False)-baseline)

#returns the first absolute maxiumum of the event
def max_val(
    data: np.ndarray,
    var: list,
    baseline: float,
):
    data = data[var[3]:var[4]]    
    maxi = np.nanmax(data)
    if isinstance(maxi, list):
        return maxi[0] - baseline
    else:
        return maxi - baseline
    
#returns the first absolute miniumum of the event
def min_val(
    data: np.ndarray,
    var: list,
    baseline: float,
):
    data = data[var[3]:var[4]]
    data = data[var[3]:var[4]]    
    mini = np.nanmin(data)
    if isinstance(mini, list):
        return mini[0]-baseline
    else:
        return mini - baseline

#shows the length of a series of event data (to help selection a range for the functions before)
def event_length(
    file: str,
    channel_data_dir: str,
    event: int = 0,
    read_length: int = 10,
):
    for lh5_obj, entry, n_rows in LH5Iterator(file, channel_data_dir ,buffer_len=1):
        """2
        print(lh5_obj.nda)
        """
        print(len(lh5_obj.nda[0]))
        if 'event' in locals():
            print(lh5_obj.nda[0][event])
        
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