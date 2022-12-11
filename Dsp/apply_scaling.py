from pygama.lgdo import LH5Store,ls ,ArrayOfEqualSizedArrays
from pygama.lgdo import ls
import numpy as np
import json

def multiply(
    val: float,
    num1: float,
    num2: float,
):
    return val/(num1 - num2)

def scaling(
    lh5_file: list[str],
    calibration_file: dict[list[float]],
    dir: str,
    
    
):
    with open(calibration_file, 'r') as openfile:
        calibration = json.load(openfile)
        
    cmap = open("/mnt/atlas01/projects/legend/data/com/raw/2022-04-13-sipm-test/channel-map.json")
    channel_map = json.load(cmap)
    channel_dict = {}
    for i in channel_map["hardware_configuration"]["channel_map"]:
        channel_dict [i] = channel_map["hardware_configuration"]["channel_map"][i]["det_id"]
    
    for i in ls(lh5_file):
        if i == "dsp_info":
            continue
        store = LH5Store()
        obj = store.read_object("/"+i+"/dsp/"+dir,lh5_file)
        if channel_dict[i] == "NA" or channel_dict[i] == 'OB-16' or channel_dict[i] =='OB-30' or channel_dict[i] =='LLAMA-S1' or channel_dict[i] =='LLAMA-S2' or channel_dict[i] =='LLAMA-S3':
            continue
        val = calibration[channel_dict[i]]
        
        #shows how good the plot is IMPORTANT
        """
        print(val)
        a = val[1][1]-val[0][1]
        print(a)
        print(val[0][1]-a)
        """
        data = obj[0].nda
        
        scalor = np.vectorize(multiply)
        
        data = ArrayOfEqualSizedArrays( nda = scalor(data,val[1][1],val[0][1]))
              
        store.write_object(data, name=dir+"_pe",group = "/"+i+"/dsp/",lh5_file=lh5_file,wo_mode="overwrite") 
        
                

