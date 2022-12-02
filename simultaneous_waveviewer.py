import matplotlib.pyplot as plt
import os, json
import pint
import pandas
import math
import pygama.lgdo.lh5_store as lh5
from pygama.vis.waveform_browser import WaveformBrowser

def simul_viewer(
    lh5_file_in: str | list[str],
    include_channel: list[str] = ["OB-01","OB-02","OB-03","OB-05"],
    entry: list[int] =  [0],
    lines: str | list[str] = "waveform",
    y_lim: tuple[float | str | pint.Quantity] = None, #some data needs returns an error if no area is given
    x_lim: tuple[float | str | pint.Quantity] = None,
    size: tuple[float] = (14, 4),
    stacked_view: bool = True,
    data_dir: str = "raw",
    linestyle: str = "-",
    mul_width: int = 3,
    mul_figsize: tuple[int]= (20,10),
       
    base_path: str = "",
    entry_list: list[int] | list[list[int]] = None,
    entry_mask: list[int] | list[list[int]] = None,
    dsp_config: str = None,
    database: str | dict = None,
    aux_values: pandas.DataFrame = None,
    styles: dict[str, list] | str = None,
    legend: str | list[str] = None,
    legend_opts: dict = None,
    n_drawn: int = 1,
    x_unit: pint.Unit | str = None,
    norm: str = None,
    align: str = None,
    buffer_len: int = 128,
    block_width: int = 8,
    ):
    
    plt.rcParams["figure.figsize"] = size
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["font.size"] = 12
    
    #creates Dictionary for Channelnames
    file = open("/mnt/atlas01/projects/legend/data/com/raw/2022-04-13-sipm-test/channel-map.json")
    channel_map = json.load(file)
    
    channel_dict = {}
    for i in channel_map["hardware_configuration"]["channel_map"]:
        channel_dict[channel_map["hardware_configuration"]["channel_map"][i]["det_id"]] = i
    
    channel=[channel_dict[i]+data_dir for i in include_channel]
        
    length= len(channel)*len(entry)
    colourpalette = [('#'+format(round((255/length)*i), '02x')+format(round(255-(255/length)*i), '02x')+'96') for i in range(length)]
    
    if not isinstance(lh5_file_in, list):
        lh5_file = [lh5_file_in for i in channel]
    else:
        lh5_file = lh5_file_in
    
    browserlist = []
    for j,b in enumerate(entry):
        for i,a in enumerate(channel):
            legend = include_channel[i]+" "+str(b)
            browserlist.append(WaveformBrowser(
                files_in=lh5_file[i],
                lh5_group=a,
                styles=[{'ls':[linestyle], 'c':[colourpalette[i+(len(channel))*j]]}],
                y_lim=y_lim,
                x_lim=x_lim,
                base_path = base_path,
                entry_list = entry_list,
                entry_mask = entry_mask,
                dsp_config = dsp_config,
                database = database,
                aux_values = aux_values,
                lines = lines,
                legend = legend,
                legend_opts = legend_opts,
                n_drawn = n_drawn,
                x_unit = x_unit,
                norm = norm,
                align = align,
                buffer_len = buffer_len,
                block_width = block_width,
            ))
            
    mul_width = 3
    mul_figsize = (30,10)
    if not stacked_view:
        fig, axs = plt.subplots(ncols=mul_width, nrows=math.ceil(len(channel)/mul_width), figsize=mul_figsize,layout="constrained")
    for j,b in enumerate(entry):
        for i,a in enumerate(channel):
            
            if stacked_view:
                browserlist[i+(len(channel))*j].draw_entry(b,False,False)
                if i+(len(channel))*j < len(browserlist)-1:
                    browserlist[i+(len(channel))*j+1].set_figure(browserlist[0])
            
            if not stacked_view:
                browserlist[i+(len(channel))*j].set_figure(fig = fig, ax = axs[math.floor(i/mul_width),i%mul_width])
                browserlist[i+(len(channel))*j].draw_entry(b,False,False)              
    if stacked_view:                 
        return browserlist[0]
    if stacked_view:                 
        return fig, axs

