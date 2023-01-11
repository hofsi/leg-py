import os, json
import pygama.lgdo.lh5_store as lh5
from pygama.lgdo import LH5Iterator
import numpy as np
import pandas as pd
from pygama.lgdo.lh5_store import show
from pygama.lgdo.lh5_store import ls
import sys
import multiprocessing
import math
from scipy.optimize import curve_fit
from time import time


def calc_histogram(
    file,
    cdd,
    q,
    trigger: float = 1000,
    var: float = 100
    ):
    pe_eny = []
    for lh5_obj, entry, n_rows in LH5Iterator(file, cdd ,buffer_len=1000):
        for i in lh5_obj['energies'].nda:
            for m in i:
                if not(np.isnan(m)):
                    pe_eny.append(m)

    q.put(np.histogram(pe_eny,10000,range = (0,1000)))

"""
#Speed Test:

def calc_histogram(
    file,
    cdd,
    q,
    
    ):
    pe_eny = []
    dt1 = time()
    dt5=dt6=dt7=dt8=dt10 = 0
    for lh5_obj, entry, n_rows in LH5Iterator(file, cdd ,buffer_len=1):
        dt2 = time()
        for j,m in enumerate(lh5_obj['energies'].nda[0]):
            dt3 = time()
            if not(np.isnan(m)) :
                dt4 = time()
                pe_eny.append(m)
                dt5 += time()-dt4
            dt6 += time() -dt3
        dt7 += time() -dt2
    dt8 += time() -dt1
    
    print("The Iter needed " + str(dt8-dt7))
    print("The Enum needed " + str(dt7-dt6))
    print("The ifno needed " + str(dt6-dt5))
    print("The appe needed " + str(dt5))
    dt9 = time()
    hist = np.histogram(pe_eny,1000,range = (0,100))
    dt10 += time() -dt9
    print("The hist needed " + str(dt10))
    q.put(hist)
"""
    
    
    
def create_spectrum(
    file_list: list[str],
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
    

    pe_histograms = []

    for file in file_list:
        ctx = multiprocessing.get_context('spawn')
        process = []
        q = []

        pe_histogram = []
        for i,cdd in enumerate(channel_data_dir):
            q.append(ctx.Queue())
            process.append(multiprocessing.Process(target=calc_histogram,args=(file,cdd,q[i])))
            process[i].start()
        for i,_ in enumerate(channel_data_dir):
            pe_histogram.append(q[i].get())
            process[i].join()
            print("Process for "+ str(include_channel[i])+ " "+ str(file) + " has finished" )
        pe_histograms.append(pe_histogram)
    return pe_histograms

def add_together(
    pe_histograms: list[list[int]],
    scaling: list[float],               #Raw Results File
):
    com_hist = np.zeros(600)
    
    for i in range(len(pe_histograms)):                 #File
        for j in range(len(pe_histograms[i])):          #Channel
            for k, val in enumerate(pe_histograms[i][j][1]):
                a = round((val / (scaling[j][1][1]-scaling[j][0][1]))*100)      
                if a >= 0 and a < 600:
                    com_hist[a] += pe_histograms[i][j][0][k]
                    
     
    return com_hist
    

def gaus(x,a,b,c):
    return a * np.exp(-1*((x-b)**2)/(2*c**2))

def fit_gaus(
    histogramm,
    borders,
    scaling
    ):
    result = []
    convidence = []
    p0 = [4000,10,2]
    p1 = [5000,20,2]
    for i,j in enumerate(histogramm):
        sys.stdout.write('\r' + str(i+1)+"/"+str(len(histogramm)))
        res0, conv0 = curve_fit(gaus,j[1][(borders[i][0]*scaling):(borders[i][1]*scaling)],j[0][(borders[i][0]*scaling):(borders[i][1]*scaling)],p0,maxfev=100000)
        res1, conv1 = curve_fit(gaus,j[1][(borders[i][2]*scaling):(borders[i][3]*scaling)],j[0][(borders[i][2]*scaling):(borders[i][3]*scaling)],p1,maxfev=100000)
        result.append([res0.tolist(),res1.tolist()])
        convidence.append([conv0.tolist(),conv1.tolist()])       
    return result, convidence
    