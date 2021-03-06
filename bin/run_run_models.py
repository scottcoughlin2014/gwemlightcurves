
import os, sys
import glob
import numpy as np

models = ["barnes_kilonova_spectra","ns_merger_spectra","kilonova_wind_spectra","ns_precursor_Lbol","tanaka_compactmergers","macronovae-rosswog"]

for model in models:
    files = glob.glob("../data/%s/*"%model)
    for file in files:
        name = file.replace("_AB","").split("/")[-1].split(".")[0]

        filename = "../output/%s/%s.dat"%(model,name)
        if os.path.isfile(filename): continue

        system_call = "python run_models.py --doAB --model %s --name %s"%(model,name)
        os.system(system_call)

models = ["barnes_kilonova_spectra","ns_merger_spectra","kilonova_wind_spectra","macronovae-rosswog"]

#models = ["barnes_kilonova_spectra"]

for model in models:
    files = glob.glob("../data/%s/*"%model)
    for file in files:
        name = file.replace("_AB","").split("/")[-1].split(".")[0]

        filename = "../output/%s/%s_spec.dat"%(model,name)
        if os.path.isfile(filename): continue
        system_call = "python run_models.py --doSpec --model %s --name %s"%(model,name)
        #os.system(system_call)

