import sys, os
import ROOT
import pandas as pd
import numpy as np
from math import sqrt
from itertools import islice
import PhenoAnalysis_core as PA
pd.set_option('display.expand_frame_repr', False)
ROOT.gROOT.ProcessLine('.include /home/dan/DELPHES/Delphes-3.4.1/')
ROOT.gROOT.ProcessLine('.include /home/dan/DELPHES/Delphes-3.4.1/external')
ROOT.gSystem.Load('libDelphes')
import settings
import observables_builtin as obsbi
from observables_custom import calc_obs

def PrintEvent(event):
    # event.Show() #LISTS ALL INFO
    print "\nEvent info\n-------"
    for i,muon in enumerate(event.Muon):
        print "Muon {}: {},{}".format(i,muon.P4().E(), muon.Charge)
    for i,jet in enumerate(event.Jet):
        print "Jet {}: {},{}".format(i,jet.P4().E(), jet.Charge)
    for i,track in enumerate(event.Track):
        print "Track {}: {},{}".format(i,jet.P4().E(), jet.Charge)

def datExists(obj, LoadEvents):
    for f in os.listdir('./data/'):
        if f.startswith(obj.flabel+'_') and f.endswith('_obs_'+str(obj.filetype)+'.dat.gz'):
            if [int(s) for s in f.split('_') if s.isdigit()][0] >= LoadEvents:
                return True       
    return False


def readROOT(args):
    """Will parse root file into ROOTData object"""
    filename,LoadEvents,label,type,model,plotStyle,recalc = args

    luminosity = settings.globDict['Lumi']
    Energy = settings.globDict['Energy']
    process = settings.globDict['Procs']
    observables = settings.globDict['ObsNames']
    mode = settings.globDict['mode']

    print "Reading ROOT file: "+str(filename)
    
    myfile=ROOT.TFile(filename)
    mytree=myfile.Delphes

    # WHAT ABOUT ADDING CUSTOM BRANCHES OR ENTIRELY CUSTOM TREE DEF? 
    # https://root-forum.cern.ch/t/pyroot-adding-a-branch-to-a-tree/2918/2
    # https://root.cern.ch/gitweb/?p=root.git;a=blob;f=tutorials/pyroot/staff.py;h=d955e2ca7481a9a507cb40dbb71c2f85ac12bbbc;hb=HEAD
    # e.g for single leaf var:
    # mytree.Branch('myvar', myvar, 'myvar/D')

    numberOfEntries = mytree.GetEntries()
    if LoadEvents > numberOfEntries:
        print "Cannot load more events than contained in ROOT file!"
        print "Loading",str(numberOfEntries)
        print ""
        LoadEvents=numberOfEntries

    obj = PA.PAData('ROOT',numberOfEntries,LoadEvents,luminosity,Energy,label,type,model,process,plotStyle)
    # modify below to check dataframe.keys() contains all observables required, ifnot then compute just that column and append.
    if datExists(obj, LoadEvents) and recalc==False:
        # check if dat file with rows > LoadEvents exists
        datFilename = getDatName(obj, LoadEvents)
        obj.readObs(Nrows=LoadEvents,datFilename=datFilename)
    else:
        if mode=="Builtin":
            # NEW TESTS##########
            obsObjs={}
            for obs in observables:
                obsObjs[obs] = obsbi.Observable(obs)
            #######################

        for event in islice(mytree,LoadEvents): 
            #event.Jet=event.GenJet  #test these events with no detector smearing of particles
            process.preselection(event)
            if process.selection(event):
                #print event.Muon[0].IsolationVar
                #if event.Muon[0].IsolationVar>0.0001: continue
                # print dir(event.Jet.At(0))
                # print dir(event.Jet.At(0).Constituents)
                # event.Jet.At(0).Constituents.Print()
                # exit()
                # for c in event.Jet.At(0).Constituents:
                #     print c
                # print "\n\n\n"
                # print event.Jet.At(0).Particles.GetObjectInfo
                # exit()
                #PrintEvent(event)
                #branches=[event.Jet.At(0),event.Jet.At(1),event.Muon.At(0)] # this should be changed depending on process
                
                # CHECK BELOW WEIGHT IS CORRECT
                observ = { 'EventWeight' : event.Event.At(0).Weight*luminosity*1000/LoadEvents }
                for obs in observables:
                    if mode=="Custom":
                        observ[obs] = calc_obs(Energy,obs,event,process.proc_label)
                    if mode=="Builtin":       
                        observ[obs] = obsObjs[obs].calc(event)  
            
                    obj.obs=obj.obs.append(observ, ignore_index=True)
                del observ
        obj.saveObs()

    del myfile
    del mytree

    return obj
