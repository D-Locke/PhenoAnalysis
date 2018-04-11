import sys, os
import ROOT
import pandas as pd
import numpy as np
from math import sqrt
from observables import calc_obs
from itertools import islice
pd.set_option('display.expand_frame_repr', False)
ROOT.gSystem.Load('libDelphes')

class ROOTData:
    """Object containing metadata of root file, and observables dataframe"""
    def __init__(self,Nentries,LoadEvents,luminosity,label,type,model,process,plotStyle):
        self.filetype='ROOT'
        self.Nentries=Nentries      # this is how many events stored in full .ROOT file
        self.LoadEvents=LoadEvents # this is how many to load
        self.luminosity=luminosity
        self.obs=pd.DataFrame()  # for shoving in dataframe containing observables - SHOULD INSTEAD CREATE METHODS TO HAVE OBSERVABLES IN EACH EVENT CLASS!
        self.events=[]
        self.label=label
        self.type=type # e.g "signal" or "background"
        self.process=process
        self.model=model
        self.plotStyle=plotStyle


    @property
    def Nevents(self):
        """ for number of detector level events remaining after cuts """
        if len(self.obs) < 1:
            Nevents=0
        else:
            Nevents=sum(self.obs["EventWeight"])
        return Nevents

    @property
    def Xsec(self):
        if len(self.obs) < 1:
            Xsec=0
        else:
            Xsec=sum(self.obs["EventWeight"])/(self.luminosity)
        return Xsec

    def __str__(self):
        return ("\n{label} \n===========\nTotal Number of MC events: {events}"
            "\nLuminosity: {lum}fb^-1"
            "\nTotal CrossSection [fb]: {totXsec}\nProcess CrossSection[fb]: {Xsec}\n"
            "Observables:\n {obs}".format(label=self.label,
                                                       events=self.LoadEvents,
                                                       lum=self.luminosity,
                                                       totXsec=self.totXsec,
                                                       Xsec=self.Xsec,
                                                       obs=self.obs.head()))
    def saveObs(self):
        self.obs.to_csv('./data/'+self.label+'_'+str(self.LoadEvents)+'_obs_root.dat', sep='\t',index=False)

 
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

    obj = ROOTData(numberOfEntries,LoadEvents,luminosity,label,type,model,process,plotStyle)

    # modify below to check dataframe.keys() contains all observables required, ifnot then compute just that column and append.
    if os.path.isfile('./data/'+obj.label+'_'+str(obj.LoadEvents)+'_obs.dat'):
        print "\nDataframe already stored, loading {file} ...\n".format(file='./data/'+obj.label+'_'+str(obj.LoadEvents)+'_obs_root.dat')
        obj.obs=pd.read_csv('./data/'+obj.label+'_'+str(obj.LoadEvents)+'_obs.dat', sep='\t')
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
    # total cross section assumes equal weights i.e calchep
    obj.totXsec=obj.obs["EventWeight"][0]*obj.LoadEvents/(obj.luminosity)

    return obj
