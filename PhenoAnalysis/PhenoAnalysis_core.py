import sys, os
from math import sqrt
import multiprocessing

from LHEreader import *
from ROOTreader import *
from observables import *
from plotting import *

class PAData:
    """Object containing metadata of root file, and observables dataframe"""
    def __init__(self,filetype,Nentries,LoadEvents,luminosity,label,type,model,process,plotStyle):
        self.filetype=filetype
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
        self.ObsFilename=self.ObsFilename()


    @property
    def Nevents(self):
        """ for number of detector level events remaining after cuts """
        if len(self.obs) < 1:
            Nevents=0
        else:
            Nevents=sum(self.obs["EventWeight"])
        return Nevents

    @property
    def totXsec(self):
        if len(self.obs) < 1:
            totXsec=0
        else:
            totXsec=self.obs["EventWeight"][0]*self.LoadEvents/(self.luminosity)
        return totXsec

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
    def ObsFilename(self):
        return './data/'+self.label+'_'+str(self.LoadEvents)+'_obs_'+str(self.filetype)+'.dat.gz'

    def saveObs(self):
        self.obs.to_csv(self.ObsFilename, sep='\t',index=False)

    def readObs(self):
        print "\nDataframe already stored, loading {file} ...\n".format(file=self.ObsFilename)
        self.obs=pd.read_csv(self.ObsFilename, compression='gzip',sep='\t')


class Logger:
    """ For logging console output to text file"""
    def __init__(self,filename):
        self.terminal = sys.stdout
        open(filename, 'w').close() #clear previous run
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass    

def parallel_readROOT(args):
    """parallelizes reading of .root and storage of observables dataframe"""
    sys.stdout = Logger("./cutNplot/ROOT/RUN_INFO.log")
    p = multiprocessing.Pool()
    objects = p.map(readROOT, args)
    p.close()
    p.join()
    for obj in objects:
        print obj
    return objects

# def parallel_readLHE(args):
#     return [readLHE(args[0]),readLHE(args[1])]

def parallel_readLHE(args):
    """parallelizes reading of .root and storage of observables dataframe"""
    sys.stdout = Logger("./cutNplot/LHE/RUN_INFO.log")
    p = multiprocessing.Pool()
    objects = p.map(readLHE, args)
    p.close()
    p.join()
    for obj in objects:
        print obj
    return objects


def ApplyCuts(objects, observable, limits):
    """hacky way, would be better to act on event objects than this obs dataframe!"""
    low=limits[0]
    high=limits[1]
    efficiencies={}
    print observable+' cut\t'+'['+str(low)+','+str(high)+']\n'
    for obj in objects:
        before=obj.Nevents 
        obj.obs = obj.obs[obj.obs[observable]>low]
        obj.obs = obj.obs[obj.obs[observable]<high]
        # print cutObs.head()
        print "\n\n"
        print "\t"+str(obj.label)
        print "\t-----------------------"
        after=obj.Nevents
        print "\tEvents    : "+str(after)+'/'+str(before)
        print "\tXsec [fb] : "+str(after/obj.luminosity)+'/'+str(before/obj.luminosity)
        if before!=0:
            Efficiency=after/before
        else:
            Efficiency=-1
        print "\tEfficiency: ",str(Efficiency)
        efficiencies[obj.label]=Efficiency
    return efficiencies


def significance(s,b):
    return s/sqrt(s+b)

def cutNplot(objects, cuts,**kwargs):
    #events of this decay chain:
    PlotCuts=kwargs.get('PlotCuts',False)
    decEvents={}
    for obj in objects:
        decEvents[obj.label]=obj.Nevents

    AllEff={}
    quickPlot(objects ,"NoCuts")
    Dalitz(objects ,"NoCuts")
    for i,cut in enumerate(cuts):
        print "\nAPPLYING CUT "+str(i+1)+": \n**************************"
        AllEff[cut]=ApplyCuts(objects, cut, cuts[cut])
        if PlotCuts==True:
            quickPlot(objects , cut+"Cut")
            Dalitz(objects , cut+"Cut")

    print "\n\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "TOTALS: \n"
    for obj in objects:
        print obj.label+': '
        totalEff=float(len(obj.obs))/decEvents[obj.label]
        print "\tEvents: "+str(obj.Nevents)+'/'+str(decEvents[obj.label])
        print "\tEfficiency:"+str(float(obj.Nevents)/decEvents[obj.label])
        print ""
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n"

    cutEvents={}
    for obj in objects:
        cutEvents[obj.label]=obj.Nevents

    print "\n############################################################"
    print "\nSIGNIFICANCES: "
    for obj in objects:
        if obj.type=="signal":
            BGevents=0
            decBGevents=sum(decEvents[bg.label] for bg in objects if (bg.type=="background" and (bg.model=="SM" or bg.model==obj.model)))
            BGevents=sum(bg.Nevents for bg in objects if (bg.type=="background" and (bg.model=="SM" or bg.model==obj.model)))
            if BGevents!=0:
                print obj.label+': '
                sigEff=float(obj.Nevents)/decEvents[obj.label]
                bgEff=float(BGevents)/decBGevents
                print "\t\tSignal efficiency: "+str(sigEff)
                print "\t\tBackground efficiency: "+str(bgEff)
                signif = significance(obj.Nevents,BGevents)
                print "\t\ts/sqrt(s+b): "+str(signif)
            else:
                print "No backgrounds supplied"
    print "\n############################################################\n"






