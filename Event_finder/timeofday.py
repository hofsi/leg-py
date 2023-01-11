import json
import pygama.lgdo.lh5_store as lh5
import numpy as np






def calchour(
    minval: float,
):
    with open("fitness_avg0_625,1250.json.json", "r") as infile:
        muon_events_dic = json.load(infile)
    
    events = []
    for i in muon_events_dic:
        counter = 0
        for j in muon_events_dic[i]:
            if j[0] > minval:
                counter += 1
        events.append((i[76:83],counter))
        
    events.sort(key=lambda x: x[0])
    
    timings = []
    timestamp = []
    for i,_ in enumerate(range(len(events)-1)):

        if i > 55:
            timings.append(round((7200 + int(events[i][0][3:]))/100))
        elif i > 39:
            timings.append(round((4800 + int(events[i][0][3:]))/100))
        elif i > 17:
            timings.append(round((2400 + int(events[i][0][3:]))/100))
        else:
            timings.append(round((int(events[i][0][3:]))/100))

        timestamp.append(int(events[i][0][3:]))
        #timestamp.append(int(events[i+1][0][3:])-int(events[i][0][3:]))
        
    
    ammount = []
    for i,j in events:
        ammount.append(j)
    return ammount,timings,timestamp
   
    
    
    
    
    
    
    """
    events = []
    for i in muon_events_dic:
        events.append((i[76:83],len(muon_events_dic[i])))
        
    events.sort(key=lambda x: x[0])
    
    timings = []
    for i,_ in enumerate(range(len(events)-1)):
        timings.append(int(events[i][0][2:])-int(events[i+1][0][2:]))
    
    ammount = []
    for i,j in events:
        ammount.append(j)
    return ammount,timings
   
    """
    
    