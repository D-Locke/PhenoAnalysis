import sys, os
import ROOT
import pandas as pd
import numpy as np
from math import sqrt

import xml.etree.ElementTree as ET
import gzip
pd.set_option('display.expand_frame_repr', False)
from itertools import islice
import PhenoAnalysis_core as PA
import settings
import observables_builtin as obsbi
from observables_custom import calc_obs


""" TODO:
* Make Jet,Muon etc. classes similar to ROOT?
"""
class Particle:
    def __init__(self,pdgid,spin,px=0,py=0,pz=0,energy=0,mass=0):
        self.pdgid=pdgid
        self.PID=pdgid
        self.Px=px
        self.Py=py
        self.Pz=pz
        self.E=energy
        self.Mass=mass
        self.spin=spin
        # also add charge to allow more ROOT like definitions?

    def __str__(self):
        """ What to print when print called on Particle object """
        return ("Particle: {id} with m={mass:.2f}GeV, s={spin}."
                " P4=({E:.2f},{px:.2f},{py:.2f},{pz:.2f}), PT={pt:.2f}".format(id=self.pdgid,
                                                               mass=self.Mass,
                                                               spin=self.spin,
                                                               E=self.E,
                                                               px=self.Px,
                                                               py=self.Py,
                                                               pz=self.Px,
                                                               pt=self.PT))
        #return self.energy, self.px, self.py, self.pz

    def __lt__(self, other):
        # for quick ordering jets from high to low PT
        return self.PT < other.PT

    # to make similar to Delphes ROOT defs
    def P4(self):
        return self.p4

    @property
    def p4(self):
        return ROOT.TLorentzVector(self.Px,self.Py,self.Pz,self.E)
    
    @p4.setter
    def p4(self,value):
        self.px=value.Px()
        self.py=value.Py()
        self.pz=value.Pz()
        self.energy=value.E()
        self.mass=value.M()
    
    @property
    def P(self):
        return self.p4.P()
    
    @property
    def Eta(self):
        return self.p4.Eta()
    
    @property
    def PT(self):
        return self.p4.Pt()


class partList(list):
    """ simpler analog of tclonesarray. Here you can fill by passing kwargs and required value as list"""
    def __init__(self,*event,**kwargs):
        """ branch name required for builtin observables """
        if event:
            event=event[0]
            for part in event.Particle:
                if all(getattr(part,k) in kwargs[k] for k in kwargs):
                    self.append(part)

    def RecursiveRemove(self,obj):
        """ to match ROOT function for TClonesArray"""
        self.remove(obj)

    def GetEntries(self):
        return len(self)

    def __str__(self):
        string=""
        for p in self:
            string=string+"{}\n".format(p)
        return string

class Event:
    def __init__(self,num_particles,weight):
        self.num_particles=num_particles    # this is original number, if remove some then use GetEntries to repopulate this?
        self.Particle=partList() # renamed to be consistent with ROOT genParticle branch
        self.weight=weight
        
    
    def __addParticle__(self,particle):
        self.Particle.append(particle)
        
    def getParticlesByIDs(self,idlist):
        partlist=partList() # make analogue of TClonesArray with atleast GetEntries()
        if type(idlist) is int:
            idlist=[idlist]
        for pdgid in idlist:
            for p in self.Particle:
                if p.pdgid==pdgid:
                    partlist.append(p)
        partlist.sort(reverse=True) # sorts in place by PT
        return partlist


    def __str__(self):
        string="\nEvent ({} particles) [weight: {:.2e}]\n============\n".format(self.Particle.GetEntries(), self.weight)
        for p in self.Particle:
            string=string+"\t{}\n".format(p)
        return string

def preselection(jets,muons,process):
    if len(jets) == process["Njets"] and len(muons) == process["Nmuons"]: 
        return True
    else:
        return False


# def getelements(filename):
#     """Yield *tag* elements from *filename_or_file* xml incrementaly."""
#     context = iter(ET.iterparse(filename, events=('start', 'end')))
#     _, root = next(context) # get root element
#     for event, elem in context:
#         if event == 'end':
#             yield elem
#             root.clear() # free memory

def getNevents(xml_file):
    """ this method is slowish but generic to headers """
    context = iter(ET.iterparse(xml_file, events=('start', 'end')))
    _, root = next(context) # get root element
    Nevents=0
    for event, elem in context:
        if event == 'end' and elem.tag=='event':
            Nevents+=1
    root.clear() # free memor
    return Nevents


def getEvents(xml_file):
    """Yield *tag* elements from *filename_or_file* xml incrementaly."""
    context = iter(ET.iterparse(xml_file, events=('start', 'end')))
    _, root = next(context) # get root element
    for event, elem in context:
        if event == 'end' and elem.tag=='event':
            yield elem
            root.clear() # free memor


##################################
# SHOULD GO IN CLASS DEF FOR USE WITH ROOT

def datExists(obj, LoadEvents):
    for f in os.listdir('./data/'):
        if f.startswith(obj.flabel+'_') and f.endswith('_obs_'+str(obj.filetype)+'.dat.gz'):
            if [int(s) for s in f.split('_') if s.isdigit()][0] >= LoadEvents:
                return True       
    return False

def datHasObs(datFilename,observables):
    header = pd.read_csv(datFilename, compression='gzip',sep='\t', nrows=1).columns.values
    if sorted(header) == sorted(observables):
        return True
    else:
        print "{} does not contain all observables, recalculating... ".format(datFilename)
        return False 

def getDatName(obj, LoadEvents):
    for f in os.listdir('./data/'):
        if f.startswith(obj.flabel+'_') and f.endswith('_obs_'+str(obj.filetype)+'.dat.gz'):
            if [int(s) for s in f.split('_') if s.isdigit()][0] >= LoadEvents:
                return './data/'+f      
    return ''

##########################

def readLHE(args):
    """Will parse root file into ROOTData object"""
    filename,LoadEvents,label,type,model,plotStyle,recalc = args

    luminosity = settings.globDict['Lumi']
    Energy = settings.globDict['Energy']
    process = settings.globDict['Procs']
    observables = settings.globDict['ObsNames']
    mode = settings.globDict['mode']
    parts = settings.globDict['parts']

   



    print "Reading LHE file: "+str(filename)   

    if filename.endswith('.gz'):
        xml_open = gzip.open
    else:
        xml_open = open


    #init = root.find('init')
    # this should become metadata for a hdf5 filestore, which dataframe for different files
    # if(child.tag=='init'):
        #     """ read init info, e.g pp 7000 7000 GeV etc """
        #     #init=child.text.strip().split('\n')
        #     # part1, part2=init[0], init[1]
        #     # en1, en2 = init[2], init[3]
    
    with xml_open(filename) as xml_file:
        numberOfEntries = getNevents(xml_file)

    obj = PA.PAData('LHE',numberOfEntries,LoadEvents,luminosity,Energy,label,type,model,process,plotStyle)

    calc=True
    if datExists(obj, LoadEvents) and recalc==False:
        datFilename = getDatName(obj, LoadEvents)
        if datHasObs(datFilename, observables):        
            obj.readObs(Nrows=LoadEvents,datFilename=datFilename)
            calc=False

    if calc:
        # NEW TESTS##########
        if mode=="builtin":
            obsObjs={}
            for obs in observables:
                obsObjs[obs] = obsbi.Observable(obs)
        #######################


        with xml_open(filename) as xml_file:
            if LoadEvents > numberOfEntries:
                print "Cannot load more events than contained in LHE file!"
                print "Loading",str(numberOfEntries)
                print ""
                LoadEvents=numberOfEntries

            for child in islice(getEvents(xml_file),LoadEvents):               
                if(child.tag=='event'):
                    lines=child.text.strip().split('\n')
                    event_header=lines[0].strip()
                    num_part=int(event_header.split()[0].strip())
                    EventWeight=float(event_header.split()[2].strip())
                    event=Event(num_part, EventWeight)
                    for i in range(1,num_part+1):
                        part_data=lines[i].strip().split()
                        if int(part_data[1]) != -1: #remove incoming parts
                            p=Particle(int(part_data[0]), float(part_data[12]), float(part_data[6]), float(part_data[7]), float(part_data[8]), float(part_data[9]), float(part_data[10]))
                            event.__addParticle__(p)

                    # in python these are effectively pointers (i.e not hard copied)
                    # should just defaulty define those that match ROOT branches, rest will be filled with global partDefs
                    event.Jet  = event.getParticlesByIDs([1,2,3,4,5,-1,-2,-3,-4,-5,21])
                    event.Muon = event.getParticlesByIDs([13,-13])
                    event.Electron = event.getParticlesByIDs([11,-11])

                    for p in parts:
                        setattr(event,parts[p].branchName, partList(event, **parts[p].attr))

                    # MWTC - add "TaggedJets" which correspond to VBF jets
                    event.TaggedJet = sorted(event.Jet, key=lambda x: abs(x.Eta), reverse=True)[:2]

                    process.preselection(event)
                    if process.selection(event): 
                        observ = { 'EventWeight' : EventWeight*luminosity*1000.0/LoadEvents }

                        # print event
                        # sumEe=e[0].P4().E()+e[1].P4().E()
                        #pOut=Ws[0].p4+Ws[1].p4
                        #sumEpPz= (pOut.E()+pOut.Pz())
                        #sumEmPz= (pOut.E()-pOut.Pz())
                        # print "sqrt(sHat): {} \t max E+-Pz out: {} \t diff: {}".format(sumEe,max(sumEpPz,sumEmPz),sumEe-max(sumEpPz,sumEmPz))
                        # print "initial M : {} \t final M: {}".format((e[0].p4+e[1].p4).M(),(Ws[0].p4+Ws[1].p4).M())
                        #sumEe=500
                        #print "sqrt(sHat): {} \t max E+-Pz out: {} \t diff: {}".format(sumEe,max(sumEpPz,sumEmPz),sumEe-max(sumEpPz,sumEmPz))

                        if mode=="builtin":
                            for obs in observables:  
                                observ[obs] = obsObjs[obs].calc(event) 
                        if mode=="custom":  
                            for obs in observables:                    
                                observ[obs] = calc_obs(Energy,obs,event,process.proc_label)
                                     
                        obj.obs=obj.obs.append(observ, ignore_index=True)
             
            obj.saveObs()
    # print obj
    return obj