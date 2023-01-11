import numpy as np
from pygama.lgdo import LH5Iterator,LH5Store
import json
import matplotlib.pyplot  as plt
from pygama.vis.waveform_browser import WaveformBrowser

EVENT_DIR = "/dsp/energies_pe"
TRIGGER_DIR = "/dsp/trigger_pos"
TRIGGER_POS = 10000
TRIGGER_VARIANCE = 1000
LOWER_BORDER = 350




def find_muon_in_ep (
    lh5_file_list: list[str],
    min_ep: float = 1000,
    include_channel: list[str] = ["OB-01","OB-02","OB-03","OB-05","OB-06","OB-07","OB-08","OB-09","OB-12","OB-13","OB-14","OB-17","OB-21","OB-22","OB-23","OB-24","OB-25","OB-26","OB-28","OB-29","OB-31","OB-35","OB-36","OB-37","OB-38","OB-39","OB-40"],
    
):
    store = LH5Store()
    cmap = open("/mnt/atlas01/projects/legend/data/com/raw/2022-04-13-sipm-test/channel-map.json")
    channel_map = json.load(cmap)
    channel_dict = {}
    for i in channel_map["hardware_configuration"]["channel_map"]:
        channel_dict [channel_map["hardware_configuration"]["channel_map"][i]["det_id"]] = i
    channel_dir=[channel_dict[i] for i in include_channel]
    
    obj_pe = []
    obj_tg = []

    for lh5_file in lh5_file_list:
        for cd in channel_dir:
            obj_pe.append(store.read_object(cd + EVENT_DIR, lh5_file))
            obj_tg.append(store.read_object(cd + TRIGGER_DIR, lh5_file))


    muon_array = []
    array = []
    #print(obj_pe)
    for m in range(len(obj_pe)):
        for i in range(len(obj_pe[m][0].nda)):
            for  j,trig in enumerate(obj_tg[m][0].nda[i]):
                #if trig >= TRIGGER_POS-TRIGGER_VARIANCE and trig <= TRIGGER_POS+TRIGGER_VARIANCE:
                if obj_pe[m][0].nda[i][j] > 350:
                    if i not in array:
                        array.append(i)
                        #print(str(obj_pe[m][0].nda[i][j]) +" "+ str(trig) + " "+ str(i))  
                    
        if (m + 1)%len(include_channel) ==0:
            print("Added " + str(m))
            muon_array.append(array)
            array =  []

    print(muon_array)

    """
    #find muon event
    for lh5_file in lh5_file_list:
        for cdd in channel_data_dir:
            for lh5_obj, entry, n_rows in LH5Iterator(lh5_file, cdd + EVENT_DIR ,buffer_len=100):
                for lh5_trig_obj, entry_trig, n_rows_trig in LH5Iterator(lh5_file, cdd + TRIGGER_DIR ,buffer_len=100):
                    for a in range(len(lh5_obj)):
                        if lh5_obj.nda[a] > 
    """

def draw_high_energy_event(raw_file: str, entry: int, dsp_file: str = None, peaks: list[int] = None, size = (14,24)) -> None:
    store = LH5Store()
    
    channel_map='/mnt/atlas01/projects/legend/data/com/raw/2022-04-13-sipm-test/channel-map.json'
    with open(channel_map, 'r') as f:
        channels=list(json.load(f)['hardware_configuration']['channel_map'].keys())
  
    fig=plt.figure(figsize=size)
    ax=fig.subplots(11,3)
    for i,ch in enumerate(channels):
        ax[i//3,i%3].set_xticklabels([])
        ax[i//3,i%3].set_xlabel('')
        ax[i//3,i%3].set_ylabel('')
        ax[i//3,i%3].plot([0],[0], label=ch)
        #Drawing waveforms
        browser = WaveformBrowser(raw_file, ch+'/raw', styles=[{'c':['k']}])
        browser.set_figure(fig=fig, ax=ax[i//3,i%3])
        browser.draw_entry(entry, clear=False)
        #Drawing vertical lines
        if bool(dsp_file):
            peak_pos=store.read_object(ch+'/dsp/trigger_pos', dsp_file, idx=[entry])[0].nda[0]
            peak_pos=peak_pos[peak_pos>0]
            for x in peak_pos:
                if x!=0:
                    ax[i//3,i%3].axvline(x=x*16, ymin=0, ymax=1, color='red', ls='--', lw=0.75)
        if bool(peaks):
            peak_pos=peaks
            for x in peak_pos:
                if x!=0:
                    ax[i//3,i%3].axvline(x=x*16, ymin=0, ymax=1, color='red', ls='--', lw=0.75)
        ax[i//3,i%3].legend(prop={'size':8})  
   
