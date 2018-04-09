import sys, os
import ROOT
import pandas as pd
import numpy as np
from math import sqrt
from observables import calc_obs
import xml.etree.ElementTree as ET


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
        partlist=[]
        for pdgid in idlist:
            for p in self.particles:
                if p.pdgid==pdgid:
                    partlist.append(p)
        return partlist


class LHEData:
    """Object containing metadata of root file, and observables dataframe"""
    def __init__(self,Nentries,LoadEvents,luminosity,label,type,model,process,plotStyle):
        self.filetype='LHE'
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
        return ("\n{label} \n===========\nTotal Number of events: {events}"
            "\nTotal CrossSection [fb]: {totXsec}\nProcess CrossSection[fb]: {Xsec}\n"
            "Observables:\n {obs}".format(label=self.label,
                                                       events=self.LoadEvents,
                                                       totXsec=self.totXsec,
                                                       Xsec=self.Xsec,
                                                       obs=self.obs.head()))
    def saveObs(self):
        self.obs.to_csv('./data/'+self.label+'_'+str(self.LoadEvents)+'_obs_lhe.dat', sep='\t',index=False)

    
    def __addEvent__(self,event):
        self.events.append(event)
     
    def clearEvents(self):
        del self.events

    def getParticlesByIDs(self,idlist):
        partlist=[]
        for event in self.events:
            partlist.extend(event.getParticlesByIDs(idlist))
        return partlist


def readLHE(args):
    """Will parse root file into ROOTData object"""
    name,LoadEvents,luminosity,label,type,model,process,observables,plotStyle = args

    tree = ET.parse(name)
    root = tree.getroot()
    
    numberOfEntries = len(root)
    obj = LHEData(numberOfEntries,LoadEvents,luminosity,label,type,model,process,plotStyle)
    print "\n\nReading LHE file...\n"

    eventCounter=0
    for eventCounter,child in enumerate(root):
        if LoadEvents > numberOfEntries:
            print "Cannot load more events than contained in LHE file!"
            print "Loading",str(numberOfEntries)
            print ""
            LoadEvents=numberOfEntries

        if(child.tag=='event') and (eventCounter<LoadEvents):
            lines=child.text.strip().split('\n')
            event_header=lines[0].strip()
            num_part=int(event_header.split()[0].strip())
            EventWeight=float(event_header.split()[2].strip())
            e=Event(num_part)
            for i in range(1,num_part+1):
                part_data=lines[i].strip().split()
                p=Particle(int(part_data[0]), float(part_data[12]), float(part_data[6]), float(part_data[7]), float(part_data[8]), float(part_data[9]), float(part_data[10]))
                e.__addParticle__(p)
            obj.__addEvent__(e)

    if os.path.isfile('./data/'+obj.label+'_'+str(obj.LoadEvents)+'_obs_lhe.dat'):
        print "\nDataframe already stored, loading {file} ...\n".format(file='./data/'+obj.label+'_'+str(obj.LoadEvents)+'_obs_lhe.dat')
        obj.obs=pd.read_csv('./data/'+obj.label+'_'+str(obj.LoadEvents)+'_obs_lhe.dat', sep='\t')
    else:
        for event in obj.events:
            jets = event.getParticlesByIDs([1,2,3,4,5,6,-1,-2,-3,-4,-5,-6])
            muons=event.getParticlesByIDs([13])
            if len(jets) == process["Njets"] and len(muons) == process["Nmuons"]:
                observ = { 'EventWeight' : EventWeight*luminosity*1000/LoadEvents }
                for obs in observables:
                #JET1,JET2,MUON = partList
                    parts = jets+muons
                    observ[obs] = calc_obs(obs,parts)              
                obj.obs=obj.obs.append(observ, ignore_index=True)
        obj.saveObs()

    del obj.events[:]
    obj.totXsec=obj.obs["EventWeight"][0]*obj.LoadEvents/(obj.luminosity)
    print obj
    return obj