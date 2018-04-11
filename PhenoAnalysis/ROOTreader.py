import sys, os
import ROOT
import pandas as pd
import numpy as np
from math import sqrt
from observables import calc_obs
from itertools import islice
import PhenoAnalysis_core as PA
pd.set_option('display.expand_frame_repr', False)
ROOT.gSystem.Load('libDelphes')

def readROOT(args):
    """Will parse root file into ROOTData object"""
    filename,LoadEvents,luminosity,label,type,model,process,observables,plotStyle = args

    print "Reading ROOT file: "+str(filename)
    
    myfile=ROOT.TFile(filename)
    mytree=myfile.Delphes 

    numberOfEntries = mytree.GetEntries()
    if LoadEvents > numberOfEntries:
        print "Cannot load more events than contained in ROOT file!"
        print "Loading",str(numberOfEntries)
        print ""
        LoadEvents=numberOfEntries

    obj = PA.PAData('ROOT',numberOfEntries,LoadEvents,luminosity,label,type,model,process,plotStyle)

    # modify below to check dataframe.keys() contains all observables required, ifnot then compute just that column and append.
    if os.path.isfile(obj.ObsFilename):
        obj.readObs()
    else:
        for event in islice(mytree,LoadEvents):
            if event.Jet.GetEntries() == process["Njets"] and event.Muon.GetEntries() == process["Nmuons"]:
                branches=[event.Jet.At(0),event.Jet.At(1),event.Muon.At(0)] # this should be changed depending on process
                observ = { 'EventWeight' : event.Event.At(0).Weight*luminosity*1000/LoadEvents }
                for obs in observables:
                    observ[obs] = calc_obs(obs,branches)              
                obj.obs=obj.obs.append(observ, ignore_index=True)
        obj.saveObs()

    del myfile
    del mytree

    return obj
