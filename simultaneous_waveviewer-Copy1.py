import matplotlib.pyplot as plt
import os, json
import pint
import pygama.lgdo.lh5_store as lh5
from pygama.vis.waveform_browser import WaveformBrowser

def simul_viewer(
    lh5_file: str | list[str],
    include_channel: list[str] = ["OB-01","OB-02","OB-03","OB-05"],
    entry: int | list[int] = 0,
    lines: str | list[str] = "waveform",
    y_lim_correction: tuple[float | str | pint.Quantity] = [9800,10600],
    x_lim_correction: tuple[float | str | pint.Quantity] = [0,450000],
    size: tuple[float] = (14, 4),
    stacked_view: bool = True,
    data_dir: str = "raw",
    
    lh5_group: str,
    base_path: str = "",
    entry_list: list[int] | list[list[int]] = None,
    entry_mask: list[int] | list[list[int]] = None,
    dsp_config: str = None,
    database: str | dict = None,
    aux_values: pandas.DataFrame = None,
    lines: str | list[str] = "waveform",
    styles: dict[str, list] | str = None,
    legend: str | list[str] = None,
    legend_opts: dict = None,
    n_drawn: int = 1,
    x_unit: pint.Unit | str = None,
    x_lim: tuple[float | str | pint.Quantity] = None,
    y_lim: tuple[float | str | pint.Quantity] = None,
    norm: str = None,
    align: str = None,
    buffer_len: int = 128,
    block_width: int = 8,

    
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
        channel.append(channel_dict[i]+'/'+data_dir)
        
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
        if not stacked_view:
            plt.show()
    return ;

