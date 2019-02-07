import sys, os
import ROOT
import pandas as pd
import numpy as np
from math import sqrt
from observables import calc_obs
import xml.etree.ElementTree as ET
import gzip
pd.set_option('display.expand_frame_repr', False)
from itertools import islice
import PhenoAnalysis_core as PA
import settings
import observables_lhe as obslhe

""" TODO:
* Make Jet,Muon etc. classes similar to ROOT?
"""
class Particle:
    def __init__(self,pdgid,spin,px=0,py=0,pz=0,energy=0,mass=0):
        self.pdgid=pdgid
        self.px=px
        self.py=py
        self.pz=pz
        self.energy=energy
        self.mass=mass
        self.spin=spin
        # also add charge to allow more ROOT like definitions?

    def __str__(self):
        """ What to print when print called on Particle object """
        return ("Particle: {id} with m={mass:.2f}GeV, s={spin}."
                " P4=({E:.2f},{px:.2f},{py:.2f},{pz:.2f}), PT={pt:.2f}".format(id=self.pdgid,
                                                               mass=self.mass,
                                                               spin=self.spin,
                                                               E=self.energy,
                                                               px=self.px,
                                                               py=self.py,
                                                               pz=self.px,
                                                               pt=self.pt))
        #return self.energy, self.px, self.py, self.pz

    def __lt__(self, other):
        # for quick ordering jets from high to low PT
        return self.pt < other.pt

    def P4(self):
        return self.p4

    @property
    def p4(self):
        return ROOT.TLorentzVector(self.px,self.py,self.pz,self.energy)
    
    @p4.setter
    def p4(self,value):
        self.px=value.Px()
        self.py=value.Py()
        self.pz=value.Pz()
        self.energy=value.E()
        self.mass=value.M()
    
    @property
    def p(self):
        return self.p4.P()
    
    @property
    def eta(self):
        return self.p4.Eta()
    
    @property
    def pt(self):
        return self.p4.Pt()

class partList(list):
    """ wrapper for list objects to make analogous to ROOT TClonesArray """
    def __init__(self, *args):
        list.__init__(self, *args)
        #self.name = 'Muon'

    def GetEntries(self):
        """ ROOTlike """
        return len(self)

    def __str__(self):
        string=""
        for p in self:
            string=string+"{}\n".format(p)
        return string

class Event:
    def __init__(self,num_particles,weight):
        self.num_particles=num_particles    # this is original number, if remove some then use GetEntries to repopulate this?
        self.particles=partList()
        self.weight=weight
        
    
    def __addParticle__(self,particle):
        self.particles.append(particle)
        
    def getParticlesByIDs(self,idlist):
        partlist=partList() # make analogue of TClonesArray with atleast GetEntries()
        if type(idlist) is int:
            idlist=[idlist]
        for pdgid in idlist:
            for p in self.particles:
                if p.pdgid==pdgid:
                    partlist.append(p)
        partlist.sort(reverse=True) # sorts in place by PT
        return partlist


    def __str__(self):
        string="\nEvent ({} particles) [weight: {:.2e}]\n============\n".format(self.particles.GetEntries(), self.weight)
        for p in self.particles:
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

def datExists(obj, LoadEvents):
    for f in os.listdir('./data/'):
        if f.startswith(obj.flabel+'_') and f.endswith('_obs_'+str(obj.filetype)+'.dat.gz'):
            if [int(s) for s in f.split('_') if s.isdigit()][0] >= LoadEvents:
                return True       
    return False

def getDatName(obj, LoadEvents):
    for f in os.listdir('./data/'):
        if f.startswith(obj.flabel+'_') and f.endswith('_obs_'+str(obj.filetype)+'.dat.gz'):
            if [int(s) for s in f.split('_') if s.isdigit()][0] >= LoadEvents:
                return './data/'+f      
    return ''

def readLHE(args):
    """Will parse root file into ROOTData object"""
    filename,LoadEvents,label,type,model,plotStyle,recalc = args

    luminosity = settings.globDict['Lumi']
    Energy = settings.globDict['Energy']
    process = settings.globDict['Procs']
    observables = settings.globDict['ObsNames']
    mode = settings.globDict['mode']


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

    if datExists(obj, LoadEvents) and recalc==False:
        datFilename = getDatName(obj, LoadEvents)
        obj.readObs(Nrows=LoadEvents,datFilename=datFilename)
    else:
        # NEW TESTS##########
        if mode=="Builtin":
            obsObjs={}
            for obs in observables:
                obsObjs[obs] = obslhe.Observable(obs)
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
                    event.Jet  = event.getParticlesByIDs([1,2,3,4,5,-1,-2,-3,-4,-5,21])
                    event.Muon = event.getParticlesByIDs([13,-13])
                    event.Ws= event.getParticlesByIDs([24,-24])
                    event.Wp= event.getParticlesByIDs(24)
                    event.Wm= event.getParticlesByIDs(-24)
                    # event.e= event.getParticlesByIDs([11,-11])
                    # MWTC - add "TaggedJets" which correspond to VBF jets
                    event.TaggedJet = sorted(event.Jet, key=lambda x: abs(x.eta), reverse=True)[:2]

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

                        for obs in observables:
                        #JET1,JET2,MUON = partList
                            if mode=="Custom":
                                observ[obs] = calc_obs(Energy,obs,event,process.proc_label)
                            if mode=="Builtin":
                                observ[obs] = obsObjs[obs].calc(event)                
                        obj.obs=obj.obs.append(observ, ignore_index=True)

             
            obj.saveObs()
    print obj
    return obj