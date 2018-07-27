import sys, os
import ROOT
import pandas as pd
import numpy as np
from math import sqrt
from observables import calc_obs
import xml.etree.ElementTree as ET
pd.set_option('display.expand_frame_repr', False)
from itertools import islice
import PhenoAnalysis_core as PA

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

    def __str__(self):
        """ What to print when print called on Particle object """
        return ("Particle, {id} with m={mass}GeV, s={spin}."
                " Four momentum::({E},{px},{py},{pz})".format(id=self.pdgid,
                                                               mass=self.mass,
                                                               spin=self.spin/2,
                                                               E=self.energy,
                                                               px=self.px,
                                                               py=self.py,
                                                               pz=self.px))
        #return self.energy, self.px, self.py, self.pz

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
    
    
class Event:
    def __init__(self,num_particles):
        self.num_particles=num_particles
        self.particles=[]
        
    
    def __addParticle__(self,particle):
        self.particles.append(particle)
        
    def getParticlesByIDs(self,idlist):
        partlist=[] # make analogue of TClonesArray with atleast GetEntries()
        for pdgid in idlist:
            for p in self.particles:
                if p.pdgid==pdgid:
                    partlist.append(p)
        return partlist

def preselection(jets,muons,process):
    if len(jets) == process["Njets"] and len(muons) == process["Nmuons"]: 
        return True
    else:
        return False

def readLHE(args):
    """Will parse root file into ROOTData object"""
    name,LoadEvents,luminosity,Energy,label,type,model,process,observables,plotStyle,recalc = args

    print "Reading LHE file: "+str(name)

    #if name[-2:]==".gz": #write functions to deal with zipped files


    tree = ET.parse(name)
    root = tree.getroot()    
    numberOfEntries = len(root)
    
    obj = PA.PAData('LHE',numberOfEntries,LoadEvents,luminosity,Energy,label,type,model,process,plotStyle)

    if os.path.isfile(obj.ObsFilename) and recalc==False:
        obj.readObs()
    else:
        for child in islice(root,LoadEvents):
            if LoadEvents > numberOfEntries:
                print "Cannot load more events than contained in LHE file!"
                print "Loading",str(numberOfEntries)
                print ""
                LoadEvents=numberOfEntries

            if(child.tag=='event'):
                lines=child.text.strip().split('\n')
                event_header=lines[0].strip()
                num_part=int(event_header.split()[0].strip())
                EventWeight=float(event_header.split()[2].strip())
                event=Event(num_part)
                for i in range(1,num_part+1):
                    part_data=lines[i].strip().split()
                    p=Particle(int(part_data[0]), float(part_data[12]), float(part_data[6]), float(part_data[7]), float(part_data[8]), float(part_data[9]), float(part_data[10]))
                    event.__addParticle__(p)

                event.Jet  = event.getParticlesByIDs([1,2,3,4,5,6,-1,-2,-3,-4,-5,-6])
                event.Muon = event.getParticlesByIDs([13,-13])

                if process.preselection(event): 
                    observ = { 'EventWeight' : EventWeight*luminosity*1000/LoadEvents }
                    for obs in observables:
                    #JET1,JET2,MUON = partList
                        observ[obs] = calc_obs(Energy,obs,event,process.proc_label)              
                    obj.obs=obj.obs.append(observ, ignore_index=True)
         
        obj.saveObs()
    del tree
    del root

    return obj