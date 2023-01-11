import json
import pygama.lgdo.lh5_store as lh5
import numpy as np


store=lh5.LH5Store()

def values_within_parameters(
    data: list[list[float]],
    time_data: list[list[float]],
    event: int,
    min_val: float,
    
):
    found_fitting_event = False
    fitting_event_time = []
    for k,i in enumerate(data):    
        for l,j in enumerate(i[event]):
            if j > min_val: 
                found_fitting_event = True
                fitting_event_time.append(time_data[k][l])
    return found_fitting_event,fitting_event_time

def corralation(
    files: list[str],
    include_channel: list[str] = ["OB-01","OB-02","OB-03","OB-05","OB-06","OB-07","OB-08","OB-09","OB-12","OB-13","OB-14","OB-17","OB-21","OB-22","OB-23","OB-24","OB-25","OB-26","OB-28","OB-29","OB-31","OB-35","OB-36","OB-37","OB-38","OB-39","OB-40"],
    search_area: float = 0.001,
    min_val: float = 10,
    min_fit: float = 1000,
    measurement_length: float = 0.00006
):
    with open("fitness.json", "r") as infile:
        muon_events_dic = json.load(infile)
    
    cmap = open("/mnt/atlas01/projects/legend/data/com/raw/2022-04-13-sipm-test/channel-map.json")
    channel_map = json.load(cmap)
    channel_dict = {}
    for i in channel_map["hardware_configuration"]["channel_map"]:
        channel_dict[channel_map["hardware_configuration"]["channel_map"][i]["det_id"]] = i
        
    channel_data_dir=[channel_dict[i]+"/dsp/" for i in include_channel]
    
    time_stamps_list = []
    events_nr_dict = {}
    rejected_events = {}
    
    for file in files:
        #Load Data
        dsp_file = "/mnt/atlas01/users/shofinger/dsp_6/" + file[70:85] + ".lh5"
        muon_events_file = muon_events_dic[file]  
        timings = store.read_object("/ch002/raw/timestamp",file)[0].nda

        
        #Selects events of sufficant fitness
        muon_events = []
        for i in muon_events_file:
            if i[0] > min_fit:
                muon_events.append(i)
        #Creates list of timestamps for muon events
        muon_events_time = []
        for i in muon_events:
            muon_events_time.append(timings[i[1]])
            


        #Load events from dsp file
        hc_events = []
        hc_timings = []
        for cdd in channel_data_dir:
            events = store.read_object(cdd + "energies_pe",dsp_file)
            hc_timestamps = store.read_object(cdd + "energies_pe",dsp_file)
            hc_events_tmp = []
            hc_timestamps_tmp = []
            for i in events[0].nda:
                hc_events_tmp.append(i) 
            for i in hc_timestamps[0].nda:
                hc_timestamps_tmp.append(i)
            hc_events.append(hc_events_tmp)       
            hc_timings.append(hc_timestamps_tmp)
        
        time_stamps = []
        events_nr = []
        rejected_nr = []
        
        for k,muon_event in enumerate(muon_events):
            for j,i in enumerate(timings[muon_event[1]+1:]):
               
                if i > timings[muon_event[1]]+measurement_length and i < timings[muon_event[1]]+search_area:
                   
                    print("Found Event " +str(np.where(timings == i)))
                    if  True:
                        found_event,timestamps = values_within_parameters(hc_events,hc_timings,j,min_val)
                        print(timestamps)
                        if found_event:
                            print("Event was accepted")
                            for p in timestamps:
                                time_stamps.append(p-timings[muon_event[1]])
                                events_nr.append(np.where(timings == i))
                    else:
                        rejected_nr.append(np.where(timings == i))
                        break
                if i > timings[muon_event[1]]+search_area:
                    break
        
        events_nr_dict[file] = events_nr
        rejected_events[file] = rejected_nr
        time_stamps_list += time_stamps
    return time_stamps_list,events_nr_dict,rejected_events
            
            
"""
 for m in range(1,10):
                        if i-timings[muon_event[1]] == 4.792213439941406e-05 *m:
                            a += 1
                            counter = 1
                        elif i-timings[muon_event[1]] == 9.608268737792969e-05 *m:
                            b += 1
                            counter = 1
                        elif i-timings[muon_event[1]] == 4.8160552978515625e-05 *m:
                            c += 1
                            counter = 1
"""