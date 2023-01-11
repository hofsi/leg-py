import json
import pygama.lgdo.lh5_store as lh5
import numpy as np


store=lh5.LH5Store()

def values_within_parameters(
    data: list[list[list[float]]],
    event: int,
    min_val: float,
    
):
    found_fitting_event = False
    fitting_event_time = []
    for i in data:    
        for j in i[event]:
            if j[0] > min_val and not np.isnan(j[1]): 
                found_fitting_event = True
                fitting_event_time.append(j[1])
    return found_fitting_event,fitting_event_time



def corralation(
    files: list[str],
    include_channel: list[str] = ["OB-01","OB-02","OB-03","OB-05","OB-06","OB-07","OB-08","OB-09","OB-12","OB-13","OB-14","OB-17","OB-21","OB-22","OB-23","OB-24","OB-25","OB-26","OB-28","OB-29","OB-31","OB-35","OB-36","OB-37","OB-38","OB-39","OB-40"],
    search_area: float = 0.001,
    min_val: float = 10,
    min_fit: float = 10000,
    measurement_length: float = 0.00005,
    max_average_needed: float = 3000,
):
    
    with open("fitness_avg_0_3000.json", "r") as infile:
        average_dic = json.load(infile)
        
    with open("fitness_avg0_625_1250.json", "r") as infile:
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
        average_file = average_dic[file]
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
            
        #load timestamps for raw file
        raw_timestamp = store.read_object("/ch002/raw/waveform/dt",file)[0].nda[0]

        #Load events from dsp file
        dsp_events = []
        for cdd in channel_data_dir:
            hc_events = store.read_object(cdd + "energies_pe",dsp_file)
            hc_timestamps = store.read_object(cdd + "trigger_pos",dsp_file)
            events_tmp = []
            for i,j in enumerate(hc_events[0].nda):
                
                events_tmp.append((j,hc_timestamps[0].nda[i]))
            dsp_events.append(events_tmp)       
       
        time_stamps = []
        events_nr = []
        rejected_nr = []
        
        for muon_event in muon_events:
            for j,i in enumerate(timings[muon_event[1]+1:]):
                
                """print(j+1+muon_event[1])
                print(np.where(timings == i))
                print(" ")"""
                
                if i > timings[muon_event[1]]+measurement_length and i < timings[muon_event[1]]+search_area:
                    print("found event")
                    #print("Found Event " +str(np.where(timings == i)))
                    if not i in muon_events_time:
                        found_event,timestamps = values_within_parameters(dsp_events,j+1+muon_event[1],min_val)
                        #print(timestamps)
                        if average_file[j+1+muon_event[1]] > max_average_needed:
                            if found_event:
                                #print("Event was accepted")
                                for p in timestamps:
                                    if not j+1+muon_event[1] in events_nr:
                                        time_stamps.append((p)*raw_timestamp*0.000000001+i-timings[muon_event[1]])
                                        events_nr.append(j+1+muon_event[1])
                    else:
                        print("muon in muon found")
                        rejected_nr.append(j+1+muon_event[1])
                        break
                if i > timings[muon_event[1]]+search_area:
                    break
        
        events_nr_dict[file] = events_nr
        rejected_events[file] = rejected_nr
        time_stamps_list += time_stamps
        print("Finished File: "+file)
    return time_stamps_list,events_nr_dict,rejected_events
            