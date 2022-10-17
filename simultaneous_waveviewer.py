import matplotlib.pyplot as plt
import os, json
import pint
import pygama.lgdo.lh5_store as lh5
from pygama.vis.waveform_browser import WaveformBrowser

def simul_viewer(
    lh5_file: str = "/mnt/atlas01/projects/legend/data/com/raw/2022-04-13-sipm-test/run007/a/20220417-113433-m6-muon-amajl4-mmaj3-es30000.lh5",
    include_channel: list[str] = ["OB-01","OB-02","OB-03","OB-05"],
    entry: int | list[int] = 0,
    y_lim_correction: tuple[float | str | pint.Quantity] = [9800,10600],
    x_lim_correction: tuple[float | str | pint.Quantity] = [0,450000],
    size: tuple[float] = (24, 10),
) -> None:
    
    plt.rcParams["figure.figsize"] = size
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["font.size"] = 12
    
    #creates Dictionary for Channelnames
    file = open("/mnt/atlas01/projects/legend/data/com/raw/2022-04-13-sipm-test/channel-map.json")
    channel_map = json.load(file)
    
    channel_dict = {};
    for i in channel_map["hardware_configuration"]["channel_map"]:
        channel_dict[channel_map["hardware_configuration"]["channel_map"][i]["det_id"]] = i
    
    channel = [];
    for i in include_channel:
        channel.append(channel_dict[i]+'/raw')
        
    colourpalette = []
    for i in range(len(channel)):
        colourpalette.append('#'+format(round(255/len(channel)*i), '02x')+format(round(255-255/len(channel)*i), '02x')+'96')

    browserlist = []
    for i,a in enumerate(channel):
        browserlist.append(WaveformBrowser(lh5_file,a,styles=[{'ls':['--'], 'c':[colourpalette[i]]}],y_lim=y_lim_correction,x_lim=x_lim_correction))

    for i,a in enumerate(browserlist):
        browserlist[i].draw_entry(entry,False,False) 
        if i < len(browserlist)-1:
            browserlist[i+1].set_figure(browserlist[i])
    return ;

