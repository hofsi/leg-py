import os, json
import pygama.lgdo.lh5_store as lh5
from pygama.lgdo import LH5Iterator
import numpy as np
import pandas as pd
import matplotlib as plt
from pygama.lgdo.lh5_store import show
from pygama.lgdo.lh5_store import ls
import sys
import multiprocessing
import math
from scipy.optimize import curve_fit


def calc_histogram(
    file,
    cdd,
    q,
    
    ):
    pe_eny = []
    for lh5_obj, entry, n_rows in LH5Iterator(file, cdd ,buffer_len=1):   
        for j,m in enumerate(lh5_obj['energies'].nda[0]):
            if not(np.isnan(m)) :
                pe_eny.append(m)
    q.put(np.histogram(pe_eny,1000,range = (0,100)))

def create_spectrum(
    file,
    include_channel: list[str] = ["OB-01","OB-02","OB-03","OB-05","OB-06","OB-07","OB-08","OB-09","OB-12","OB-13","OB-14","OB-16","OB-17","OB-21","OB-22","OB-23","OB-24","OB-25","OB-26","OB-28","OB-29","OB-30","OB-31","OB-35","OB-36","OB-37","OB-38","OB-39","OB-40"],
    data_dir: str = "/dsp",
    simul_process: int = 1, 
    
    ):
    
    #creates dictionary and selects channels form input channel names
    cmap = open("/mnt/atlas01/projects/legend/data/com/raw/2022-04-13-sipm-test/channel-map.json")
    channel_map = json.load(cmap)
    channel_dict = {}
    for i in channel_map["hardware_configuration"]["channel_map"]:
        channel_dict[channel_map["hardware_configuration"]["channel_map"][i]["det_id"]] = i
    channel_data_dir=[channel_dict[i]+data_dir for i in include_channel]
    
    ctx = multiprocessing.get_context('spawn')
    pe_histograms = []
    process = []
    pe_eny = []
    q = []
    for i,cdd in enumerate(channel_data_dir):
        q.append(ctx.Queue())
        process.append(multiprocessing.Process(target=calc_histogram,args=(file,cdd,q[i])))
        process[i].start()
    for i,_ in enumerate(channel_data_dir):
        pe_histograms.append(q[i].get())
        process[i].join()
        print("Process for "+ str(include_channel[i])+ " has finished" )
    return pe_histograms



"""
sys.stdout.write('\r' +"working on " +str(include_channel[i]) +" " + str(i+1)+"/"+str(len(channel_data_dir)))
        
for lh5_obj, entry, n_rows in LH5Iterator(file, cdd ,buffer_len=1):
           
            for j,m in enumerate(lh5_obj['energies'].nda[0]):
                if not(np.isnan(m)) :
                    pe_eny.append(m)
            
            if not(np.isnan(lh5_obj['energies'].nda[0][0])) :
                    pe_eny.append(lh5_obj['energies'].nda[0][0])
            
"""

def gaus(x,a,b,c):
    return a * math.exp(-((x-b)**2)/(2*c**2))

def fit_gaus(
    histogramm,
    borders,
    ):
    result = []
    convidence = []
    for i,j in enumerate(hostogramm):
        res0, conv0 = curve_fit(gaus,j[1][borders[i][0]:borders[i][1]],j[1][borders[i][0]:borders[i][1]])
        res1, conv1 = curve_fit(gaus,j[1][borders[i][0]:borders[i][1]],j[1][borders[i][0]:borders[i][1]])
        result.append([res0,res1])
        convidence.append([conv0,conv1])
    return result, convidence
    