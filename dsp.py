import pygama.dsp.build_dsp as build_dsp
import simultaneous_waveviewer

"""
    build_dsp prosseses a LH5 file given via "f_raw" to a "f_dsp" output file.
    it needs a "dsp_config" file which is a dictionary that discribes which and how the prossesors from /pygama/dsp/processors should be used.
    n_max is used to limit the number of waveforms to be processed.
    chan_config gets a JSON file with all channel names in lh5_tables
    (complete list of input variables can be found in /pygama/dsp/build_dsp.py)
"""
def dsp():
    
    build_dsp(
        f_raw = "/mnt/atlas01/projects/legend/data/com/raw/2022-04-13-sipm-test/run008/20220425-175437-th228-4p7kbq-8400-athr200,12,2-es4000.lh5",
        f_dsp = "/home/ge25qer/lh5/test.lh5",
        dsp_config = "/home/ge25qer/pygama/tests/dsp/configs/sipm-dsp-config.json",
        n_max = 4,
    )

    simultaneous_waveviewer.simul_viewer(lh5_file = "/home/ge25qer/lh5/test.lh5", data_dir = "dsp")
    return;
