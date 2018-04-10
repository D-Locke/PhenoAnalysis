import sys, os
import ROOT
import pandas as pd
import numpy as np
from math import sqrt
from observables import calc_obs
pd.set_option('display.expand_frame_repr', False)

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
            "\nTotal CrossSection [fb]: {totXsec}\nProcess CrossSection[fb]: {Xsec}\n"
            "Observables:\n {obs}\nLuminosity: {lum}fb^-1".format(label=self.label,
                                                       events=self.LoadEvents,
                                                       totXsec=self.totXsec,
                                                       Xsec=self.Xsec,
                                                       obs=self.obs.head(),
                                                       lum=self.luminosity))
    def saveObs(self):
        self.obs.to_csv('./data/'+self.label+'_'+str(self.LoadEvents)+'_obs_root.dat', sep='\t',index=False)


def readROOT(args):
    """Will parse root file into ROOTData object"""
    name,LoadEvents,luminosity,label,type,model,process,observables,plotStyle = args

    print "Reading ROOT file: "+str(name)
    
    ROOT.gSystem.Load("libDelphes")
    chain = ROOT.TChain("Delphes")
    chain.Add(name)    
    # Create object of class ExRootTreeReader
    treeReader = ROOT.ExRootTreeReader(chain)
    numberOfEntries = treeReader.GetEntries()
    if LoadEvents > numberOfEntries:
        print "Cannot load more events than contained in ROOT file!"
        print "Loading",str(numberOfEntries)
        print ""
        LoadEvents=numberOfEntries


    obj = ROOTData(numberOfEntries,LoadEvents,luminosity,label,type,model,process,plotStyle)

    # Get pointers to branches used in this analysis
    branchJet = treeReader.UseBranch("Jet")
    branchMuon= treeReader.UseBranch("Muon")
    branchMissingET=treeReader.UseBranch("MissingET")
    branchEvent = treeReader.UseBranch("Event")
    #EventWeight = 657.18*lumin/numberOfEntries


    # modify below to check dataframe.keys() contains all observables required, ifnot then compute just that column and append.
    if os.path.isfile('./data/'+obj.label+'_'+str(obj.LoadEvents)+'_obs.dat'):
        print "\nDataframe already stored, loading {file} ...\n".format(file='./data/'+obj.label+'_'+str(obj.LoadEvents)+'_obs_root.dat')
        obj.obs=pd.read_csv('./data/'+obj.label+'_'+str(obj.LoadEvents)+'_obs.dat', sep='\t')
    else:
        for entry in range(0, LoadEvents):
            # Load selected branches with data from specified event
            treeReader.ReadEntry(entry)
            MissingET=branchMissingET.At(0)
            if branchJet.GetEntries() == process["Njets"] and branchMuon.GetEntries() == process["Nmuons"]:
                # JET1=branchJet.At(0), JET2=branchJet.At(1), MUON=branchMuon.At(0)
                branches=[branchJet.At(0),branchJet.At(1),branchMuon.At(0)]
                EventWeight = branchEvent.At(0).Weight
                observ = { 'EventWeight' : EventWeight*luminosity*1000/LoadEvents }
                for obs in observables:
                    observ[obs] = calc_obs(obs,branches)              
                obj.obs=obj.obs.append(observ, ignore_index=True)
            obj.saveObs()

    del chain
    del treeReader
    # total cross section assumes equal weights i.e calchep
    obj.totXsec=obj.obs["EventWeight"][0]*obj.LoadEvents/(obj.luminosity)

    return obj
